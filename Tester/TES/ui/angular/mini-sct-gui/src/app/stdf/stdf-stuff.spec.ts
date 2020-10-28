import {stdfGetValue, StdfRecord, StdfRecordType} from './stdf-stuff';

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
