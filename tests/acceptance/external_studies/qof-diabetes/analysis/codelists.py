from ehrql import codelist_from_csv


# Cluster name: DM_COD
# Description: Diabetes mellitus codes
# Refset ID: ^999004691000230108
dm_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dm_cod.csv",
    column="code",
)

# Cluster name: DMRES_COD
# Description: Diabetes resolved codes
# Refset ID: ^999003371000230102
dmres_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmres_cod.csv",
    column="code",
)

# Cluster name: DMINVITE_COD
# Description: Invite for diabetes care review codes
# Refset ID: ^999012371000230109
dminvite_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dminvite_cod.csv",
    column="code",
)

# Cluster name: DMMAX_COD
# Description: Codes for maximum tolerated diabetes treatment
# Refset ID: ^999010651000230109
dmmax_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmmax_cod.csv",
    column="code",
)

# Cluster name: DMPCAPU_COD
# Description: Codes for diabetes quality indicator care unsuitable for patient
# Refset ID: ^999010731000230107
dmpcapu_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmpcapu_cod.csv",
    column="code",
)

# Cluster name: IFCCHBAM_COD
# Description: IFCC HbA1c monitoring range codes
# Refset ID: ^999003251000230103
ifcchbam_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ifcchbam_cod.csv",
    column="code",
)

# Cluster name: MILDFRAIL_COD
# Description: Mild frailty diagnosis codes
# Refset ID: ^999013531000230106
mildfrail_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-mildfrail_cod.csv",
    column="code",
)

# Cluster name: MODFRAIL_COD
# Description: Moderate frailty diagnosis codes
# Refset ID: ^999013571000230108
modfrail_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-modfrail_cod.csv",
    column="code",
)

# Cluster name: SERFRUC_COD
# Description: Serum fructosamine codes
# Refset ID: ^999005691000230107
serfruc_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-serfruc_cod.csv",
    column="code",
)

# Cluster name: SEVFRAIL_COD
# Description: Severe frailty diagnosis codes
# Refset ID: ^999012131000230109
sevfrail_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-sevfrail_cod.csv",
    column="code",
)

# Cluster name: BLDTESTDEC_COD
# Description: Codes indicating the patient has chosen not to receive a blood test
# Refset ID: ^999011611000230101
bldtestdec_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-bldtestdec_cod.csv",
    column="code",
)


# Cluster name: DMPCADEC_COD
# Description: Date the patient most recently chose not to receive diabetes quality
# indicator care up to and including the achievement date.
# Refset ID: ^999010691000230104
dmpcadec_cod = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-dmpcadec_cod.csv",
    column="code",
)
