# The Metis library

## Mythology [🔗](https://en.wikipedia.org/wiki/Metis_(mythology))
Metis (/ˈmiːtɪs/; Greek: Μῆτις, "<ins>wisdom</ins>," "<ins>skill</ins>," or "<ins>craft</ins>"), in ancient Greek religion, was a mythical Titaness belonging to the second generation of Titans.

By the era of Greek philosophy in the 5th century BC, Metis had become the <ins>mother of wisdom</ins> and <ins>deep thought</ins>, but her name originally connoted "<ins>magical cunning</ins>" and was as easily equated with the <ins>trickster powers</ins> of Prometheus as with the "[royal metis](https://en.wikipedia.org/wiki/Metis_(mythology)#cite_note-Brown-1)" of Zeus. The Stoic commentators allegorised Metis as the embodiment of "<ins>prudence</ins>", "<ins>wisdom</ins>" or "<ins>wise counsel</ins>", in which form she was inherited by the [Renaissance](https://en.wikipedia.org/wiki/Metis_(mythology)#cite_note-2).

## Description

In ONE STDF file ther is a lot of data that is static over all the devices. Therefore, making a pandas data-frame from ONE STDF file will yield
a lot of columns that contain identical info over the rows, and thus ends up consuming unnecessary memory space.
The Metis object thus has 2 data frames, one `static` and one `dynamic` data frame.
On a Metis object, one can:
  - `pull-in` : one or more columns from the static dataframe in the dynamic dataframe.
  - `push-out` : selected columns (or all) from the dynamic dataframe into the static dataframe (if all entries are identical!)
