export interface SingleTestResult {
  name: string;
  testNumber: number;
  result: number;
  description: string;
  units: string;
  lowerTestLimit: number;
  upperTestLimit: number;
  lowerSpecificationLimit: number;
  upperSpecificationLimit: number;
  alramDetected: boolean;
  timeoutOccurred: boolean;
  noPassFailIndication: boolean;
  testPassed: boolean;
}

export interface PartResult {
  siteNumber: number;
  headNumber: number;
  hardBin: number;
  softBin: number;
  xCoordinate: number;
  yCoordinate: number;
  testTime: number;
  executedTests: number;
  partId: string;
  partDescription: string;
  singleTestResults: Array<SingleTestResult>;
}