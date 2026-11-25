# The early pickup notice

A parcel locker service sends a pickup notice when a customer on the waitlist
gets a locker. During the evening shift, Dev received a notice at minute 10.
The operator's log says both lockers should still have been reserved.

Start with the failing shift replay. Explain which operation first puts the
service in the wrong state, reduce the incident to a focused regression test,
and fix the implementation. Keep the public API and the shift replay intact.

## Run the exercise

From the repository root, using Python 3.9 or newer and its standard library:

```sh
python3 run_tests.py
```

To run just the reported incident:

```sh
python3 run_tests.py tests.test_locker.LockerTests.test_evening_shift_replay
```

## Service contract

- The clock starts at minute 0. Only `advance` moves it. A hold assigned at
  minute 4 with a ten-minute duration expires exactly at minute 14.
- A request takes the lowest available locker. When full, the service queues
  customers in arrival order. Repeat requests preserve a customer's current
  hold or queue position.
- Cancellation removes a hold or a waitlist entry immediately. Customers can
  request again after cancelling. Cancelling an unknown customer has no effect.
- A released locker goes straight to the first waiting customer, whose full
  hold begins at the release minute. Advancing across several deadlines
  processes each one at its scheduled minute.
- `lookup` returns the customer's current hold, or `None` for a waiting or
  unknown customer. The replay uses it to check who would receive a notice.
