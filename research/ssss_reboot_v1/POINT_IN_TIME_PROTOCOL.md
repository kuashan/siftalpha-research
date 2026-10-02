# SSSS Reboot v1 — Point-in-Time Protocol

Status: **HARD CONSTRAINT / FROZEN**

For every historical bar `t`:

1. history available to the engine must be only data with timestamp <= t;
2. recompute the right-edge SSSS/XMA-dependent values using only that history;
3. store the first-observed values for bar t;
4. evaluate source state and source events for bar t;
5. persist the observation;
6. only then advance to t+1.

Forbidden:

```
compute indicator values once on full future history
-> read historical values after repainting/future dependence
-> treat them as values visible at the historical time
```

Any source component that cannot be made point-in-time reproducible must be labeled
explicitly as repainting / non-causal and cannot be used directly as an executable
signal.

## Event-time vs detection-time

Every future study must distinguish:

- event_time: when the underlying structural event occurs;
- detection_time: when the condition is actually knowable;
- execution_time: earliest realistic trade time after detection.

Forward returns anchored before detection cannot be described as executable returns.

## Execution default

Until a later asset-specific protocol freezes otherwise:

`close-confirmed information -> next tradable bar open`

No same-close execution is allowed for a close-confirmed signal.
