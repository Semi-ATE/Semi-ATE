# Toolbar

## Hardware

- Upon project opening, the most recent available hardware is 'enabled'.

- If another `hardware` is selected, `Base` and `Target` are set to the **empty string**

## Base

- Upon project opening, the `Base` is set to the **empty string**

- The rest of the `Base` list is 'PR' and 'FT'

- If one selects another `Base`, the `Target` list is updated accordingly! This means:

1. `Base` == ''

    The `Target` list is the union of **empty string**, **all** `products` and **all** `dies` for the selected `hardware`.

2. `Base` == 'PR'

    The `Target` list is the union of **empty string** and **all** `products` for the selected `hardware`

3. `Base` == 'FT'

    The `Target` list is the union of **empty string** and **all** `dies` for the selected `hardware`

## Target

- Upon project opening, the `Target` is set to the **empty string**

- The rest of the `Target` list is the union of **all** `products` and **all** `dies` for the selected `hardware` (see case Nr1 above)

- If one selects a `Target` from the list, also the `Base` that belongs to the selected `Target` is set correctly.

# Project tree view

## documentation section

Note : Skip the '**s**' at the end, I know it makes sense as we also have 'definition**s**', 'flow**s**' and 'test**s**', but 'documentation**s**' is simply not a correct english word :unamused:

The tree view under `documentation` follows the structure under project_root\documentation.

If on `spyder|project|open` we see that the project has no `documentation` subdirectory, we call the function `ATE.org.templates.documentation_templating(project_root)`, 
this function is part of the `spyder|new|project` suit of functions that create a **new project**.
In our usecase this function is 'touching up' a project that lost his documentation directory. :smirk:

## definitions section

The `definitions` section in the project tree structure **ONLY** looks at the `hardware` of the toolbar !

- `hardwaresetups` is **ALWAYS** enabled for the context menu 
- `masksets` is **ALWAYS** enabled for the context menu
- `dies` is **ONLY** available for the context menu if (for the selected hardware in the toolbar) there is at least one `maskset` defined.
- `packages` is **ALWAYS** available for the context menu
- `devices` is **ONLY** available for the context menu if (for the selected hardware in the toolbar) there is at least **ONE** 'die' defined under `dies`.
- `products` is **ONLY** available for the conext menu if (for the selected hardware in the toolbar) there is at least **ONE** 'device' defined under `devices`

## flows section

The `flows` section is **directly** related to a `Target`.
As long as no `Target` is selected, the `flows` will be disabled for the context menu.

- `flows` in case `Target` = '' 

    `flows` is not enabled for the context menu

- `flows` in case `Target` is selected and `Base` is 'PR'

    `flows` is enabled for the context menu, but there is **NO** `qualification` section !
    Ah, yes, we do `qualification` only on what we sell, and we only sell `products` !
    We do however have the `production`, `engineering`, `validation`, and `characterisation` flows !
    
- `flows` in case `Target` is selected and `Base` is 'FT'

    `flows` is enabled for the context menu **AND** the `qualification` section is available, however
    based on the `package` that is associated to the `Target` (over `device`) we have a slightly 
    different outline of the `qualification` section:

1. The `device` of the selected `Target` is associated with the 'naked die' `package`

    So, the `package` is 'virtual', this is the way we implement if we sell 'naked die' products.
    It also means that some sections in the full `qualification` section are not applicable,
    Notably everything to do with ... the package :stuck_out_tongue_winking_eye:

2. The `device` of the selected `Target` is **not** associated with the 'naked die' `package`

    So, we have a real package, and thus the full `qualification` section is available.     


### flows/production

Under `flows/production` we will find a structure as flows:



### flows/engineering

### flows/validation

### flows/characterisation

### flows/qualification







## tests section

Similar as `flows`, the `tests` section is **directly** related to a `Target`,
so again as long as no `Target` is selected the `tests` will be disabled for the context menu.

- `tests` in case `Target` == ''

    `tests` is not enabled for the context menu

- `tests` in case a `Target` is selected

    `tests` is enabled for the context menu, ofcourse with respect to the indicated `Base` ('PR' or 'FT')

The context menu on the `tests` is as follows:

- 'New Test'
- 'New Standard Test'
- 'Import Test'

## context menu on the items under 'tests' 

The context menu on the individual `test` is as follows:

- 'Open' --> open the associated `.py` file, same as double-right-click
- 'Edit' --> open the wizard, using the prior given info as a starting point.
- 'Trace' --> see where this test is used (flows/testprograms)
- 'Delete' --> delete the `.py` file, and the info from the database, as well as
removing the tests from the testprograms that use them !!!


