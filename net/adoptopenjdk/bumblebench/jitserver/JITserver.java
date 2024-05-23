package net.adoptopenjdk.bumblebench.jitserver;

import net.adoptopenjdk.bumblebench.core.MicroBench;
import net.adoptopenjdk.bumblebench.core.ThreadConfig;

import java.util.concurrent.*;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;

public final class JITserver extends MicroBench {

    // Classes and corresponding invocation counts
    private final ExecutorService pool = Executors.newFixedThreadPool(100);

    static final ThreadConfig[] doBatchRunnables;

    static {
        doBatchRunnables = option("classesToInvoc", new ThreadConfig[]{});
    }

    @Override
    protected long doBatch(long numIterations) throws InterruptedException {
        Future<?>[] futures = new Future[JITserver.doBatchRunnables.length];
        // JITServer doBatch iterations
        for (long i = 0; i < numIterations; i++) {

            // Start each thread
            for( int q = 0; q < doBatchRunnables.length; q++){
                Future<?> future = pool.submit(doBatchRunnables[q]);
                futures[q] = future;
            }

            for (Future<?> future : futures) {
                try {
                    future.get();
                } catch (ExecutionException e) {
                    System.err.println("Error in future.get()");
                    throw new RuntimeException(e);
                }
            }
        }

        return numIterations;
    }
}
