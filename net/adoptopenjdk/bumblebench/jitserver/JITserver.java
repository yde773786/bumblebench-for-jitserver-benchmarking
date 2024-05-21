package net.adoptopenjdk.bumblebench.jitserver;

import net.adoptopenjdk.bumblebench.core.MicroBench;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;

public final class JITserver extends MicroBench {

    // Classes and corresponding invocation counts
    static final ArrayList<ArrayList<Object[]>> classesToInvocation;

    // Thread to call doBatch for each kernel
    private static final class DoBatchThread implements Runnable {
        private final Method[] methodReqArr;
        private final Class<? extends MicroBench>[] classKeyArr;
        private final int[] invocationCountArr;

        // Takes in each kernel's method, class, and invocation count
        private DoBatchThread(Method[] methodReqArr, Class<? extends MicroBench>[] classKeyArr, int[] invocationCountArr) {
            this.methodReqArr = methodReqArr;
            this.classKeyArr = classKeyArr;
            this.invocationCountArr = invocationCountArr;
        }

        // Call doBatch for each kernel
        @Override
        public void run() {
            try {
                // Sequentially call the doBatch for each kernel with their corresponding invocation count.
                for(int i = 0; i < methodReqArr.length; i++) {
                    methodReqArr[i].invoke(classKeyArr[i].newInstance(), invocationCountArr[i]);
                }
            } catch (InvocationTargetException | IllegalAccessException | InstantiationException e) {
                System.err.println("Could not dynamically initiate doBatch");
                throw new RuntimeException(e);
            }
        }
    }

    static final DoBatchThread[] doBatchRunnables;

    static {
        classesToInvocation = option("classesToInvoc", new ArrayList<>());
        doBatchRunnables = new DoBatchThread[classesToInvocation.size()];

        // Create each thread
        for (int i = 0; i < classesToInvocation.size(); i++){

            ArrayList<Object[]> eachThread = classesToInvocation.get(i);

            Method[] methodReqArr = new Method[eachThread.size()];
            Class<? extends MicroBench>[] classKeyArr = new Class[eachThread.size()];
            int[] invocCountArr = new int[eachThread.size()];

            // Find Class, invocation count, and method for each kernel within thread
            int sequentialCalls = 0;
            for (Object[] classIntegerEntry : eachThread) {

                // Use Reflection to call doBatch for required number of invocations.
                Class<? extends MicroBench> classKey = (Class<? extends MicroBench>) classIntegerEntry[0];
                Integer invocationCountValue = (Integer) classIntegerEntry[1];
                Method methodReq;
                try {
                    methodReq = classKey.getDeclaredMethod("doBatch", long.class);
                } catch (NoSuchMethodException e) {
                    System.err.println("doBatch not implemented");
                    throw new RuntimeException(e);
                }
                methodReq.setAccessible(true);
                methodReqArr[sequentialCalls] = methodReq;
                classKeyArr[sequentialCalls] = classKey;
                invocCountArr[sequentialCalls] = invocationCountValue;

                sequentialCalls++;
            }

            doBatchRunnables[i] = new DoBatchThread(methodReqArr, classKeyArr, invocCountArr);
        }
    }

    @Override
    protected long doBatch(long numIterations) throws InterruptedException {

        Thread[] threads_array = new Thread[JITserver.doBatchRunnables.length];

        // JITServer doBatch iterations
        for (long i = 0; i < numIterations; i++) {

            // Start each thread
            for(int j = 0; j < doBatchRunnables.length; j++){
                threads_array[j] = new Thread(doBatchRunnables[j]);
                threads_array[j].start();
            }

            // Wait for each thread to finish
            for(Thread thread : threads_array){
                thread.join();
            }
        }

        return numIterations;
    }
}
