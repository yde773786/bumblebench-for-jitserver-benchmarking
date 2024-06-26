/*******************************************************************************
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

package net.adoptopenjdk.bumblebench.core;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;


import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import static net.adoptopenjdk.bumblebench.core.Launcher.defaultPackagePath;
import static net.adoptopenjdk.bumblebench.core.Launcher.loadTestClass;

public class Util {

	private static final Method IO_UTILS_READ_ALL_BYTES;
	private static final Method INPUT_STREAM_READ_ALL_BYTES;

	static {
		Method ioUtilsReadAllBytes = null;
		Method inputStreamReadAllBytes = null;
		try {
			try {
				Class<?> ioUtils = Class.forName("sun.misc.IOUtils");
				ioUtilsReadAllBytes = ioUtils.getDeclaredMethod(
					"readAllBytes",
					InputStream.class);
			} catch (ClassNotFoundException notFound) {
				inputStreamReadAllBytes =
					InputStream.class.getDeclaredMethod("readAllBytes");
			}
		} catch (Throwable exc) {
			throw new RuntimeException(exc);
		}

		IO_UTILS_READ_ALL_BYTES = ioUtilsReadAllBytes;
		INPUT_STREAM_READ_ALL_BYTES = inputStreamReadAllBytes;
	}

	///////////////////////////
	//
	// These statics should be initialized first because they affect option processing.
	//
	// Don't add any calls to option(...) before this point -- they will
	// probably appear to work properly, but they actually won't work quite
	// right in all circumstances.
	//
	final static String  PROPERTY_PREFIX = System.getProperty("BumbleBench.propertyPrefix", "BumbleBench.");
	final static boolean VERBOSE_OPTIONS = option("verboseOptions", true);
	final static boolean DEBUG_OPTIONS   = option("debugOptions", false);
	final static boolean LIST_OPTIONS    = option("listOptions", false);
	//
	///////////////////////////

	private static final BufferedReader _in = new BufferedReader(new InputStreamReader(System.in));
	public static BufferedReader in(){ return _in; }
	public static PrintStream out(){ return System.out; }
	public static PrintStream err(){ return System.err; }

	static final String TRUE_STRINGS  = "|t|true|yes|1||"; // Note: blank string defaults to true
	static final String FALSE_STRINGS = "|f|false|no|0|";

	public static boolean string2boolean(String value) {
		String normalized = '|' + value.toLowerCase() + '|';
		if (TRUE_STRINGS.indexOf(normalized) != -1)
			return true;
		else if (FALSE_STRINGS.indexOf(normalized) != -1)
			return false;
		else
			throw new Error("Unrecognized boolean string: \"" + value + "\"");
	}

	/*
	 * Option processing
	 */

	static String optionString(String name) {
		String result = System.getProperty(PROPERTY_PREFIX + name);
		if (VERBOSE_OPTIONS && result != null)
			out().println("  - Set option " + name + " = '" + result + "'");
		return result;
	}

	/** Returns the value of a boolean option.
	 * <p>
	 * Checks for an option property setting with the given <tt>name</tt>, and if none exists, returns the <tt>defaultValue</tt>.
	 * <p>
	 * Uses <tt>Util.string2boolean</tt> to parse the option value.
	 * <p>
	 * @see net.adoptopenjdk.bumblebench.core.Util#string2boolean
	 *
	 * @param name          the option property to search for
	 * @param defaultValue  the value to return if the given option property is not set
	 * @return              the desired option property's value
	 */
	public static boolean option(String name, boolean defaultValue) {
		if (LIST_OPTIONS)
			out().println("- Option " + name + " default " + defaultValue);
		String value = optionString(name);
		if (value == null)
			return defaultValue;
		else
			return Util.string2boolean(value);
	}

	public static String option(String name, String defaultValue) {
		if (LIST_OPTIONS)
			out().println("- Option " + name + " default " + defaultValue);
		String value = optionString(name);
		if (value == null)
			return defaultValue.intern();
		else
			return value.intern();
	}

	private static boolean isNumeric(String str)
	{
		for (char c : str.toCharArray())
		{
			if (!Character.isDigit(c)) return false;
		}
		return true;
	}

	public static ThreadConfig[] option(String name, ThreadConfig[] defaultValue){

		if (LIST_OPTIONS)
			out().println("- Option " + name + " default " + defaultValue);

		String jsonFile = optionString(name);
		ObjectMapper mapper = new ObjectMapper();
		JsonNode threads;

		try {
			threads = mapper.readTree(new File(jsonFile)).get("threads");
		} catch (IOException e) {
			throw new RuntimeException(e);
		}

		ThreadConfig[] threadConfigs = new ThreadConfig[threads.size()];
		String packagePath = option("packages", defaultPackagePath);
		String[] packages = packagePath.split("[:;]");

		for(int i = 0; i < threads.size(); i++){

			// Get each thread and initialize the arrays to store the corresponding method, class, and invocation count
			JsonNode thread = threads.get(i).get("kernels");
			Method[] methodReqArr = new Method[thread.size()];
			Class<? extends MicroBench>[] classKeyArr = new Class[thread.size()];
			int[] invocationCountArr = new int[thread.size()];

			// Get each kernel within the thread
			for(int j = 0; j < thread.size(); j++){
				JsonNode kernel = thread.get(j);

				String className = kernel.get("kernel_name").asText();
				int invocations = kernel.get("invoc_count").asInt();
				Method methodReq;
				Class<? extends MicroBench> kernelClass;

                try {
                    kernelClass = loadTestClass(packages, className);
					try {
						methodReq = kernelClass.getDeclaredMethod("doBatch", long.class);
					} catch (NoSuchMethodException e) {
						System.err.println("doBatch not implemented");
						throw new RuntimeException(e);
					}
					methodReq.setAccessible(true);
                } catch (ClassNotFoundException | IOException e) {
                    throw new RuntimeException(e);
                }

				methodReqArr[j] = methodReq;
				classKeyArr[j] = kernelClass;
				invocationCountArr[j] = invocations;
            }

			ThreadConfig threadConfig = new ThreadConfig(methodReqArr, classKeyArr, invocationCountArr);
			threadConfigs[i] = threadConfig;
		}

		return threadConfigs;
	}

	public static int option(String name, int defaultValue) {
		if (LIST_OPTIONS)
			out().println("- Option " + name + " default " + defaultValue);
		String value = optionString(name);
		if (value == null)
			return defaultValue;
		else
			return Integer.parseInt(value);
	}

	public static long option(String name, long defaultValue) {
		if (LIST_OPTIONS)
			out().println("- Option " + name + " default " + defaultValue);
		String value = optionString(name);
		if (value == null)
			return defaultValue;
		else
			return Long.parseLong(value);
	}

	public static float option(String name, float defaultValue) {
		if (LIST_OPTIONS)
			out().println("- Option " + name + " default " + defaultValue);
		String value = optionString(name);
		if (value == null)
			return defaultValue;
		else
			return Float.parseFloat(value);
	}

	public static double option(String name, double defaultValue) {
		if (LIST_OPTIONS)
			out().println("- Option " + name + " default " + defaultValue);
		String value = optionString(name);
		if (value == null)
			return defaultValue;
		else
			return Double.parseDouble(value);
	}

	/*
	 * Class loading tricks
	 */

	protected final Class loadClass(String name, byte[] bytes) {
		try {
			return new OneOffLoader(name, bytes, getClass().getClassLoader()).loadClass(name);
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	protected static Class freshlyLoadedClass(final Class original) {
		try {
			final String classFileName = "/" + original.getName().replace('.', '/') + ".class";
			final byte[] classBytes = readFully(original.getClass().getResourceAsStream(classFileName));
			return new OneOffLoader(original.getName(), classBytes, original.getClassLoader()).loadClass(original.getName());
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	private static byte[] readFully(InputStream stream) {
		try {
			if (IO_UTILS_READ_ALL_BYTES != null) {
				return (byte[])IO_UTILS_READ_ALL_BYTES.invoke(null, stream);
			} else {
				return (byte[])INPUT_STREAM_READ_ALL_BYTES.invoke(stream);
			}
		} catch (IllegalAccessException exc) {
			throw new AssertionError(exc);
		} catch (InvocationTargetException exc) {
			throw new AssertionError(exc);
		}
	}

	protected static Object newInstance(Class original) {
		return newInstanceOfPossiblyFreshlyLoadedClass(original, false);
	}

	protected static Object newInstanceOfFreshlyLoadedClass(Class original) {
		return newInstanceOfPossiblyFreshlyLoadedClass(original, true);
	}

	protected static Object newInstanceOfPossiblyFreshlyLoadedClass(Class original, boolean freshlyLoaded) {
		// Beware: if you're ever tempted to use reflection to allow you to call
		// non-public constructors (to allow the use of anonymous classes, for
		// example), just make sure you know what you're doing before choosing to
		// call setAccessible.  That method allows evil things to occur, so the
		// JIT can be expected to become conservative, which can affect performance
		// in unpredictable ways.

		try {
			if (freshlyLoaded)
				return freshlyLoadedClass(original).newInstance();
			else
				return original.newInstance();
		} catch (InstantiationException e) {
			throw new Error(e);
		} catch (IllegalAccessException e) {
			throw new Error(e);
		}
	}

	static final class OneOffLoader extends ClassLoader {

		final String _className;
		final byte[] _classBytes;

		public OneOffLoader(String className, byte[] classBytes, ClassLoader parent) {
			super(parent);
			_className  = className;
			_classBytes = classBytes;
		}

		public Class loadClass(String name) throws ClassNotFoundException {
			if (name.equals(_className)) try {
				// Don't delegate.  Re-define the class
				return defineClass(name, _classBytes, 0, _classBytes.length);
			} catch (Exception e) {
				throw new RuntimeException(e);
			}

			// Other classes, including our guy's superclass, must come from
			// the parent in order to make checkcasts etc. work properly.
			return getParent().loadClass(name);
		}

	}

}

