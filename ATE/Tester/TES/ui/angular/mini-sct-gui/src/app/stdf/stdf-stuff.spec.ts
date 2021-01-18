import {Stdf, stdfGetValue, StdfRecord, StdfRecordType} from './stdf-stuff';

describe('stdfGetValue', () => {
  it('should return undefined if key cannot be found', () => {
    let record: StdfRecord = {
      type: StdfRecordType.Ptr,
      values: [
        {key: 'a', value: 1},
        {key: 'b', value: 1},
      ]
    };
    expect(stdfGetValue(record, 'c')).toBeUndefined();
  });
});

describe('computeScaledUnits', () => {
  const SCALE_VALUE = [15, 12, 9, 6, 3, 2, -3, -6, -9, -12];
  it('should always compute expected units prefix', () => {
    let expectedUnitsPrefix = ['f', 'p', 'n', 'u', 'm', '%', 'K', 'M', 'G', 'T'];
    for (let i = 0; i < SCALE_VALUE.length; ++i) {
      let scaledUnits = Stdf.computeScaledUnits(SCALE_VALUE[i]);
      expect(scaledUnits).toEqual(expectedUnitsPrefix[i]);
    }
  });

  it('should compute "f" as prefix when the scale value is "15"', () => {
    expect(Stdf.computeScaledUnits(15)).toEqual('f');
  });

  it('should compute the empty string as prefix incase that the scale value is 0 , undefined', () => {
    expect(Stdf.computeScaledUnits(0)).toEqual('');
    expect(Stdf.computeScaledUnits(undefined)).toEqual('');
  });
});
