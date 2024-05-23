package net.adoptopenjdk.bumblebench.core;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

public class ThreadConfig implements Runnable {
    private final Method[] methodReqArr;
    private final Class<? extends MicroBench>[] classKeyArr;
    private final int[] invocationCountArr;

    // Takes in each kernel's method, class, and invocation count
    public ThreadConfig(Method[] methodReqArr, Class<? extends MicroBench>[] classKeyArr, int[] invocationCountArr) {
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
