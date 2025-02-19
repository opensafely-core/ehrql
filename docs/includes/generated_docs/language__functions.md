
<h4 class="attr-heading" id="case" data-toc-label="case" markdown>
  <tt><strong>case</strong>(<em>*when_thens</em>, <em>otherwise=None</em>)</tt>
</h4>
<div markdown="block" class="indent">
Take a sequence of condition-values of the form:
```python
when(condition).then(value)
```

And evaluate them in order, returning the value of the first condition which
evaluates True. If no condition matches, return the `otherwise` value (or NULL
if no `otherwise` value is specified).

Example usage:
```python
category = case(
    when(size < 10).then("small"),
    when(size < 20).then("medium"),
    when(size >= 20).then("large"),
    otherwise="unknown",
)
```

Note that because the conditions are evaluated in order we don't need the condition
for "medium" to specify `(size >= 10) & (size < 20)` because by the time the
condition for "medium" is being evaluated we already know the condition for "small"
is False.

A simpler form is available when there is a single condition.  This example:
```python
category = case(
    when(size < 15).then("small"),
    otherwise="large",
)
```

can be rewritten as:
```python
category = when(size < 15).then("small").otherwise("large")
```
</div>



<h4 class="attr-heading" id="maximum_of" data-toc-label="maximum_of" markdown>
  <tt><strong>maximum_of</strong>(<em>value</em>, <em>other_value</em>, <em>*other_values</em>)</tt>
</h4>
<div markdown="block" class="indent">
Return the maximum value of a collection of Series or Values, disregarding NULLs.

Example usage:
```python
latest_event_date = maximum_of(event_series_1.date, event_series_2.date, "2001-01-01")
```
</div>



<h4 class="attr-heading" id="minimum_of" data-toc-label="minimum_of" markdown>
  <tt><strong>minimum_of</strong>(<em>value</em>, <em>other_value</em>, <em>*other_values</em>)</tt>
</h4>
<div markdown="block" class="indent">
Return the minimum value of a collection of Series or Values, disregarding NULLs.

Example usage:
```python
ealiest_event_date = minimum_of(event_series_1.date, event_series_2.date, "2001-01-01")
```
</div>
