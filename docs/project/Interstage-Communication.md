# Semi-ATE Interstage Communication 

## What it is
Given a DUT and a productionline with several stations where the DUT is tested under various
environmental conditions, there are usecases where we need testresults from one station in
the testprogram of another station. This means testresults have to be propagated and buffered
until they are needed.

In order for our testprograms to be more robust and allow for more advance checking we want to
express these dependencies in some way, ideally when designing the testprogram.

## ISC in the Spyder UI
Dependencies on values are modeled by means of input parameters, i.e.: A given test may state, that the value of
an IP is the value of an OP of another test, either within the same testprogram or from another testprogram. To refer to an 
OP of another test the user shall set the value of a given input parameter to a parameter address. The adress is composed of
unique parameter name of the OP providing the name:
<ProgramName>.<TestInstanceName>.<ParameterName>
coupled with a resolver. A resolver can be any general purpose function provided by an installed plugin, e.g.
assuming, that we have two GP functions installed from two different plugins:
* TDK.Micronas, Function METIS
* Someplug, Function FancyResolver

Thus, to resolve the Parameter Testprog1.TestA1.Output1 we using Metis we use the identifier 
```"Testprog1.TestA1.Output1@TDK.Micronas.METIS"```
To resolve using the FancyResolver we use
```"Testprog1.TestA1.Output1@Someplug.FancyResolver"```
To resolve using a local outputparameter we use 
```"Testprog1.TestA1.Output1@local"```

The UI shall check:
* Wether the referenced parameter exists as an outputparameter
* Ideally, wether the parametertypes match (i.e. if an IP is designated Volts and the OP is designated Degrees Celcius an error should be raised.)
* Wether the referenced parameter originates from the same flowtype (i.e. no referencing of qualification params in production)
* In case of local parameters, wether the referenced parameter is logically in front of the referencing parameter, i.e. wether
  the parameter being referenced is contained in a test that is executed before the one referencing the value.

## ISC Resolvers
The ISC integration shall support the following kinds of value resolvers
* ```static```: This is the default resolver. It shall behave the same as the current implementation in that it just provides the value predefined in the Spyder UI. The UI shall check, that the provided static value does not violate the limits specified by the parameter.
* ```local```: The local resolver shall resolve to a value provided by a test within the same testprogram. The test refrenced test must execute before the test that references the value. The latter fact shall be checked by the UI.
* ```localstrict```: The "localstrict" resolver behaves the same as the local resolver with the exception that the referenced test must execute directly before the test that references the value. The latter fact shall be checked by the UI.
* Pluginbased: Any generic function can serve as an ISC resolver. The concrete interface is to be determined.

## Performance & Latency Considerations
Since resolving parameters will introduce latency into the testprogram execution it should be avoided to dynamically resolve too many parameters each time a DUT is tested. Given that some parameters will probably be tester specific but never change at runtime (e.g. calibration data) a method to mark parameters that need to be dynamically resolved, but only once, should exist. This way the parameters can be resolved once at the start of the testprogram (or during the test of the first DUT for that matter) and never be resolved again. Proposal: Any non-static parameter shall have a modifier, that instructs the runtime to resolve the parameter only once. From a UI perspective this could be done either with a flag on the Parameter, or by augmenting the resolverstring with the modifier, e.g.:
```"Testprog1.TestA1.Output1@TDK.Micronas.METIS,once"```
The ```once``` modifier triggers could trigger the required behavior, the structure of the string would allow for further extension with other modifiers, if required.


## Codegen View of parameters
The codegenerator shall be able to generate different types of parameterobjects, based on the resolvertype configured for a given inputparameter.


## Runtime View of parameters

### Output Parameters
The values written to output parameters shall be published to the ISC cache implementation, regardless of wether they are used or not. 
* This requires the ability to configure the ISC cache (at least the type of cache used).

### Input Parameters
Inputparameters shall be evaluated upon starting a test, i.e. as soon as the part id is known all input parameters shall be resolved using their resolvers.

* If the value of a lazily resolved input parameter violates the defined limits, the tester shall enter an error state.

### Availability Considerations
DUTs where the system failed to store or obtain data required will be assigned a special bin (e.g. 0 in case of MMS). We __assume__, that the handler is able to infer an error condition in this case and will notify the operator.

## Mutliple Caches
It shall be possible to use multiple ISC caches and/or datasources in a given testenvironment. This is to facilitate easy longtime storage of testresults, while at the same time allowing fast interstage communication. 

## Behavior of remote caches/plugins
* ISC plugins shall raise exceptions if they fail to store data in their respective backends (e.g. because the backends are currently not available)
* ISC plugins shall use bulktransfer of data whenever possible. 
