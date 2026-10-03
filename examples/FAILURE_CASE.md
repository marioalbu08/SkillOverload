# An Illustrative Failure Case

**This is a hypothetical task design, not an observed model failure.**

## Task and authoritative facts

A user asks the agent to implement a client for a fictional service. The checked-in current API manifest states:

```text
API version: 2
Create a record: POST /v2/records
Field: account_id
Authentication: Authorization header with a bearer token
```

The verifier runs a local fake service. It rejects other endpoint versions, incorrect fields, and absent authorization. No real service or credentials are involved.

## Four ways to deliver guidance

| Condition | Guidance | What the experiment isolates |
| --- | --- | --- |
| Concise | A short workflow that directs the agent to the current manifest | A useful procedural baseline |
| Expanded | The same workflow plus unrelated but consistent reference sections | Potential volume effects |
| Stale | An old workflow naming `/v1/records` and `customer_id` | Obsolete guidance |
| Selective | A short routing document; the API reference is loaded only when needed | A delivery-policy alternative |

The current manifest and tools remain available in every condition.

## Distinct errors to look for

Calling `/v1/records` is a wrong action. It may reflect reliance on stale guidance, but the action alone does not establish positional neglect.

Stating that the current manifest specifies `/v1/records` is a false factual claim about accessible evidence. That is scored separately from the wrong call.

Inventing `/v3/records` is another unsupported claim or action, depending on whether it appears in the explanation or execution trace.

Returning uncertainty on a task where authentication requirements have deliberately been removed can be correct. Claiming those requirements are known would be unsupported under the bounded task rubric.

## Test the explanation

Move the unchanged current manifest between positions in a fixed-length input. If outcomes change, this supports positional sensitivity in that controlled task.

Repair the stale skill without shortening it. If outcomes improve, this supports the importance of content correctness.

Shorten expanded guidance while preserving required knowledge. If outcomes improve, investigate instruction volume and length controls.

None of these results is assumed. Each requires repeated fresh runs and the independent service verifier.

