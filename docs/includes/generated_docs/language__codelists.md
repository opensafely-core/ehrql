
<h4 class="attr-heading" id="codelist_from_csv" data-toc-label="codelist_from_csv" markdown>
  <tt><strong>codelist_from_csv</strong>(<em>filename</em>, <em>column</em>, <em>category_column=None</em>)</tt>
</h4>
<div markdown="block" class="indent">
Read a codelist from a CSV file as either a list or a dictionary (for categorised
codelists).

_filename_<br>
Path to the file on disk, relative to the root of your repository. (Remember to use
UNIX/style/forward-slashes not Windows\style\backslashes.)

_column_<br>
Name of the column in the CSV file which contains the codes.

_category_column_<br>
Optional name of a column in the CSV file which contains categories to which each
code should be mapped. If this argument is passed then the resulting codelist will
be a dictionary mapping each code to its corresponding category. This can be passed
to the [`to_category()`](#CodePatientSeries.to_category) method to map a series of
codes to a series of categories.

For more detail see the [how-to guide](../how-to/examples.md/#using-codelists-with-category-columns).
</div>
