export function wait(ms = 1000) {
  return new Promise(resolve => {
    setTimeout(resolve, ms);
  });
}

export async function expectWaitUntil(
  fn,
  fnCondition,
  errorMessage: string,
  pollIntervall: number = jasmine.DEFAULT_TIMEOUT_INTERVAL / 10.0,
  timeout: number = jasmine.DEFAULT_TIMEOUT_INTERVAL)
  {
  let startTime = performance.now();
  let timeoutReached = false;
  while (!fnCondition()) {
    await wait(pollIntervall);
    fn();
    if (performance.now() - startTime > timeout) {
      timeoutReached = true;
      break;
    }
  }
  expect(!timeoutReached).toBe(true,errorMessage);
}
