- Complex dataset definitions may take a long time to generate patients
- ...or may not be able to generate the requested number of patients
- Certain fields will generate values that are valid in format, but are not necessarily real data. E.g. SNOMED CT codes may be generated in a valid format, but may not be real codes.
    e.g. The following will produce codes that look like SNOMED CT codes, but are randomly generated.
    Any further analysis which tries to use the code to filter or summarise data will fail to
    match expected data.
    ```
    code = clinical_events.sort_by(clinical_events.date).first_for_patient().snomedct_code
    ```
    (To some extent building up your dummy data tables can work around this sort of thing.)
- The date logic in generated dummy data might be too simplistic and hence may not reflect idiosyncrasies
in the real data.
    - For example, when ehrQL generates the `addresses` dummy table, it will ensure that the `start_date` occurs
    before the `end_date`, with both dates being between the corresponding patient's `date_of_birth` and
    `date_of_death`.
    - This makes it easier to generate a dataset that uses `addresses.for_patient_on()` with dummy tables.
    - However, the `addresses` table in the real data could be noisier than the dummy data suggests. (E.g.
    it could have a `start_date` before the patient was born, or an `end_date` occuring before a start date.)
- Semantic validity is difficult to ensure in generated dummy data
    - Certain interactions between tables/columns that should reflect reality will not necessarily be
      respected unless they are specified in the dataset definition, e.g.
        - no COVID-19 vaccines before 2020

        (Although note that such events could happen in the real data.)

    - Demographic or clinical tendencies that are expected in the cohort of interest, e.g.
        - more white people than black people in England
        - correlation between obesity and diabetes
        - statins more commonly prescribed in over 50s

Next: [Provide a dummy dataset](../provide-a-dummy-dataset/index.md)
