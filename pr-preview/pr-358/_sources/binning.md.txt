# Semi-ATE.org binning

## Definitions
* SBin: An sbin denotes a qualitymark assigned to a given dut by the software
* HBin: An hbin denotes a qualitymark assigned to a given dut, that is understood by the underlying handling system. There is a 1 * N relationship between HBins and SBins, i.e. a given HBin may have any number of SBins mapped to it.


## Binning Strategy
### Grades / Passbins
We assume 9 grades (or passbins) for each duttype, thus the SBins 1 through 9 are assumed to be good SBins, any test that grades a DUT with an SBin in this range will not cause the DUT to be treated as defective. The 9 grades range from best quality (grade 1) to lowest quality (grade 9). A DUT can only move downwards in quality during tests, i.e. a test may lower the grade of a DUT but never raise it (the system assumes a perfect DUT at the beginning and attempts to find flaws). This also means, that a DUT that was once assigned a fail bin can never be assigned a pass bin afterwards.

### Fail Bins
All bins with Id > 9 are treated as failbins. Consequently all DUTs that have one of these bins assigned shall be treated as defective. Note that the runtime will only record the first failure it encounters during evaluation of the outputparameters. This evaluation takes place in the order in which the parameters were defined in the test IDE (Spyder!). Consequently, the order in which the outputparamters are written to in the test is *not* taken into account! 
Example:
Given a test with the Ops Param1 (assigning bin 33) and Param2 (assigning bin 25), a DUT will always be assigned bin 33 if the limits of Param1 are violated, regardless of the state Param2 assumes during the test. This is even true, if Param2 is written with a failure value before Param1.

## Special Bins
We treat SBin 0 as special in that it is implicitly assigned to a DUT if a failure occurs during testing, that has nothing to do with the DUT itself, but with the testenvironment. Note that these failures will usually be unrecoverable.

## Generation of bin codes
Whenever a new outputparameter is created in the IDE this parameter shall have a (sbin!) bin code assigned. By default the next unused failbin shall be used. The user is free to change this bin to *any* other valid bin value, i.e.
- Any passbin
- Any previously defined failbin

It is explicitly allowed to use a bincode multiple times, the IDE will however not do that on its own. Each SBin that is used more than once shall be marked as such in the UI to allow the user to spot this fact easily and make sure, that it is intentionally.

Using special bin 0 is not allowed under any circumstances-


## Additional classification
In addition to being the bins, a second dimension is added to classify limitviolations. This dimension effectively controls the behavior of several flag bits in the STDF records for this DUT. For each outputparameter the user shall be given the option to specifiy wether the failure constitutes:
* A flaw (i.e. the DUT is still considered to be good, but the quality was lowered)
* An electrical failure (i.e. the DUT is bad)
* A mechanical failure (i.e. the DUT was contacted badly)
* more?

All these cases will cause the DUT to be assigned the bin that is tied to the output parameter in question (see "Binning Strategy" for details!)

The TEST_FLG bits of the PTR the outputparameter in question are set as follows
| Failure | TEST_FLG.0 | TEST_FLG.1 | TEST_FLG.2 | TEST_FLG.3 | TEST_FLG.4 | TEST_FLG.5 | TEST_FLG.6 | TEST_FLG.7 |
|---------|------------|------------|------------|------------|------------|------------|------------|------------|
| Flaw    |      o     |       o    |      o     |      o     |      o     |      o     |     o      |      o     |
| Mechanical |   o     |       o    |      o     |      o     |      o     |      x     |     x      |      -     |
| Electrical |   x     |       x    |      o     |      o     |      o     |      o     |     o      |      x     |


In addtion the three classes have the following impact on the PART_FLG of the PRR generated for the DUT

| Failure | PART_FLG.0 | PART_FLG.1 | PART_FLG.2 | PART_FLG.3 | PART_FLG.4 |
|---------|------------|------------|------------|------------|------------|
| Flaw    |      o     |       o    |      o     |      o     |      o     |
| Mechanical |   o     |       o    |      x     |      -     |      x     |
| Electrical |   o     |       o    |      o     |      x     |      o     |

with:
* o : Bit is cleared
* x : Bit is set
* \- : Bit has no specified value

Since the data in the PRR is valid for all PRRs the following policy applies to the bits in PART_FLG: All bits that were set due to the result of any subtest stay set. 


## Influence of alarms during tests 
If an alarm (a tester error due to faulty equipment) is encountered during the test, the runtime will:
* Set TEST_FLG.0 for all output parameters of the test
* Set TEST_FLG.1 for all output parameters of the test
* Set TEST_FLG.2 for all output parameters of the test
* Clear TEST_FLG.3 for all output parameters of the test
* Set TEST_FLG.4 for all output parameters of the test
* Set TEST_FLG.5 for all output parameters of the test
* Set TEST_FLG.6 for all output parameters of the test
* Set TEST_FLG.7 for all output parameters of the test (this is to make sure, that any software ignoring the value of TEST_FLG.6 will not accidently accept this DUT)
* Write the alarm type (error message?) to the ALARM_ID field of all output parameters
* Set PART_FLG.2 of the PRR for the current DUT.
* Set PART_FLG.4 of the PRR for the current DUT.


Further the runtime will abort testing of the current dut. It will not assign an SBin or an HBin (both shall be set to 0 to indicate an abnormal condition).

Motivation:
There is a conceptual mismatch in what constitutes a test in STDF and Semi-ATE.org. As such the Semi-ATE cannot reliably know which part of the output parameters are in a known good state at the time of the error. Therefore all values of this whole test are treated as invalid.

Note on exceptions:
-> Exceptions shall only be used to communicate exceptional behavior, i.e. tester errors. The tester shall !stop! in this case.
-> Additional SBin per Test, which is assigned on Alarm and Exception (?)

## Use of parameterlimits for classification
The runtime is able to dynamically resolve inputparameters to a given test. Some of these resolvers can check prerequesites (such as matching units or limits) at testdesigntime. However this is not true for a whole class of dynamic resolvers that use external services to resolve data and might not have any information about the value range the resolve date maps to. This may cause a situation where the resolved value of an inputparameter violates the testspecification (i.e. the parameterlimit!) or comes in different units than the input parameter expects. Should this happen, the runtime shall raise an alarm and abort testing the current DUT. Further the STDF record for the offending parameter shall note, that a limit violation is the source of the alarm.

Open Questions: If we assume that an alarm will send the tester in errorstate the behavior outlined above is a bit dangerous, as this will effectively stop the machine due to an error that migh just disappear for the next DUT. 

## The bintable
The mapping of an SBin to a HBin is done by means of a bintable that is generated and deployed to the tester during loading of the program. The testprogram will check if all used SBins can be mapped to a HBin and will raise an error if that is not the case. All sites of a given tester shall use the same bintable.

## Deployment of the bintable
The bintable is deployed to the tester by means of MQTT. Obtaining the bintable from whatever source was defined beforehand (e.g. jobfile) is done by the master application, as only the masterapplication has knowledge about the the format in which the information on the bintable is stored.

## Special usecases

### MMS, Multiple Sockets
The MMS protocol used by some handlers will send the (HBin!) previously assigned to a DUT along with the testcommand. This presents a problem due to the fact that we cannot know the semantics of the HBin as used by the previous testing station. It could be either, a good or a failbin. Since we don't have the bintable of the program that generated the bin we don't know. We can't even apply a heuristic such as "don't lower the bin, only increase it", since the setup of the hardbins by the handlers must assumed to be completely arbitrary.

Possible solutions:
1. Use a resultcache (such as metis!) in all cases where multiple stations are required and derive the bin kind (fail/pass) for the previous station by looking at the DUT's PRR of that station. We can use the data of the PRR to check if the HBin assigned actually constitutes a failure and can act accordingly (most importantly by not assigning a good bin in the remote case the the tests at the current station don't fail).

    Pro:
    * Will reduce the administrative efforts required to make sure bins are always in sync.
    * Removes potential for configuration mistakes.

    Con:
    * Adds additional, potentially expensive, query via ethernet for each DUT.
    * Must rely on another component in the system adding another layer of complexity.

---> This is the preferred solution

--> Assumption: There is exactly one target cache
--> There can be any number of datasources

2. One table per base per product. Effectively this means that all testprograms within the same flow (e.g. "production") and the same base (probing or final) will share a common bintable. 

    Pro:
    * Easy to implement
    * Removes all uncertainties or fuzziness as the complete binninginformation is available at all times

    Con:
    * Adds complexity for management of SBins, as all users of the system will now have to deal with all SBins for a given flow.
    * Binningtables might grow large, leading to posibly confusingly large tables on the tester UI.
