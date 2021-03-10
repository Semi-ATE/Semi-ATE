export function wait(ms = 1000) {
  return new Promise(resolve => {
    setTimeout(resolve, ms);
  });
}

export async function expectWaitUntil(
  fn,
  fnCondition,
  errorMessage: string,
  pollInterval: number = 50,
  timeout: number = 1500) {
  let startTime = performance.now();
  let timeoutReached = false;
  while (!fnCondition()) {
    await wait(pollInterval);
    if (fn)
      fn();
    if (performance.now() - startTime > timeout) {
      timeoutReached = true;
      break;
    }
  }
  expect(!timeoutReached).toBe(true,errorMessage);
}

export async function expectWhile(
  loopFunction: () => void,
  conditionFunction: () => boolean,
  onFailedMessage: string,
  checkConditionInterval: number = 100,
  timeout: number = 1500) {
    // check input parameters
    expect(timeout).toBeLessThan(jasmine.DEFAULT_TIMEOUT_INTERVAL, 'jasmine default timeout must be greater than the provided timeout');
    expect(checkConditionInterval).toBeGreaterThan(0);
    let loopNumber = timeout / checkConditionInterval;
    expect(loopNumber).toBeGreaterThan(0);

    let failed = false;
    for(let i = 0; i < timeout / checkConditionInterval; ++i) {
      if (loopFunction)
        loopFunction();
      if(!conditionFunction()) {
        failed = true;
        break;
      }
      await wait(checkConditionInterval);
    }
    expect(failed).toBe(false, onFailedMessage);
  }

export function spyOnStoreArguments(object: any, method: string, args: Array<any>): jasmine.Spy<any> {
  // As we need a function here we have to disable the only-arrow-functions rule here
  // the reason is that the this context, i.e. execution context is different from function
  // and arrow functions
  // tslint:disable:only-arrow-functions
  return spyOn<any>(object, method).and.callFake(function() {
    let idx = 0;
    args.splice(0, args.length);
    while(arguments[idx]) {
      args.push(arguments[idx]);
      idx++;
    }
  });
  // tslint:enable:only-arrow-functions
}
