"""English display labels for the German questionnaire response values.

The raw CSV keeps the original German values (data integrity); these maps
translate raw German -> English purely for charts and tables, so all
thesis-facing output is in English.
"""

# Q16 - gender
GENDER = {
    'Weiblich': 'Female',
    'Männlich': 'Male',
    'Nicht-binär': 'Non-binary',
    'Keine Angabe': 'Prefer not to say',
}
GENDER_ORDER = ['Weiblich', 'Männlich', 'Nicht-binär', 'Keine Angabe']

# Q19 - highest completed education
EDUCATION = {
    'Matura / Abitur / Hochschulreife': 'Higher ed. entrance qual. (Matura/Abitur)',
    'Bachelor': "Bachelor's degree",
    'Master': "Master's degree",
    'Lehre / Berufsausbildung': 'Vocational training',
}
EDUCATION_ORDER = ['Matura / Abitur / Hochschulreife', 'Bachelor', 'Master',
                   'Lehre / Berufsausbildung']

# Q20 - degree currently pursued
DEGREE = {
    'Bachelor': "Bachelor's",
    'Master': "Master's",
    'PhD / Doktorat': 'PhD / Doctorate',
    'Sonstige Ausbildung': 'Other education',
    'Ich strebe derzeit keinen Abschluss an': 'Not currently pursuing a degree',
}
DEGREE_ORDER = ['Bachelor', 'Master', 'PhD / Doktorat', 'Sonstige Ausbildung',
                'Ich strebe derzeit keinen Abschluss an']

# Q21 - field of study
FIELD = {
    'Betriebswirtschaft/Management': 'Business Administration/Management',
    'Volkswirtschaft': 'Economics',
    'Wirtschaftsrecht': 'Business Law',
    'Wirtschaftsinformatik': 'Business Informatics',
    'Finanzwirtschaft': 'Finance',
    'Sozial- und Geisteswissenschaften': 'Social Sciences & Humanities',
    'Naturwissenschaften': 'Natural Sciences',
    'Ingenieurwesen / Technische Wissenschaften': 'Engineering / Technical Sciences',
    'Informatik': 'Computer Science',
    'Ich studiere derzeit nicht': 'Not currently studying',
    'Sonstige': 'Other',
}

# Q22/Q23/Q24 - yes/no
YESNO = {'Ja': 'Yes', 'Nein': 'No'}

# Q18 - nationality (raw German free text -> English; normalized & deduplicated)
NATIONALITY = {
    'Deutsch': 'German', 'deutsch': 'German', 'Deutschland': 'German',
    'ger': 'German', 'German': 'German',
    'Österreich': 'Austrian', 'österreichisch': 'Austrian', 'Österreichisch': 'Austrian',
    'AT': 'Austrian', 'AUT': 'Austrian', 'Austria': 'Austrian', 'Oesterreich': 'Austrian',
    'Österrreich': 'Austrian', 'österreicherin': 'Austrian',
    'Ukraine': 'Ukrainian', 'Ukrainische': 'Ukrainian', 'Ukrainerin': 'Ukrainian',
    'Ukrainisch': 'Ukrainian',
    'Bulgarien': 'Bulgarian', 'Bulgarisch': 'Bulgarian', 'bulgarisch': 'Bulgarian',
    'Bulgarian': 'Bulgarian',
    'Russisch': 'Russian', 'Russin': 'Russian', 'Russiche Föderation': 'Russian', 'RUS': 'Russian',
    'Rumänien': 'Romanian',
    'Ungarn': 'Hungarian', 'Ungarisch': 'Hungarian', 'ungarisch': 'Hungarian', 'ungarn': 'Hungarian',
    'Slowakei': 'Slovak', 'slowakei': 'Slovak', 'Slowakisch': 'Slovak',
    'Italien': 'Italian', 'Italienisch': 'Italian', 'Italien (Südtirol)': 'Italian',
    'Indien': 'Indian',
    'türkisch': 'Turkish', 'Türkisch': 'Turkish',
    'Polnisch': 'Polish', 'Polen': 'Polish',
    'Kroatien': 'Croatian', 'Serbisch': 'Serbian', 'Schwedisch': 'Swedish',
    'Lettland': 'Latvian', 'USA': 'American', 'Luxemburgisch': 'Luxembourgish',
    'Kolumbien': 'Colombian', 'Albanien': 'Albanian', 'Tschetschenisch': 'Chechen',
    'Bosnien und Herzegowina': 'Bosnian', 'schweiz': 'Swiss', 'Kasach': 'Kazakh',
    'Portuguese': 'Portuguese', 'guatemala': 'Guatemalan', 'Guatemala City': 'Guatemalan',
    'D,NL': 'German & Dutch', 'Österreich, Kroatien': 'Austrian & Croatian',
    'AT & NL': 'Austrian & Dutch', 'bulgarisch, türkisch': 'Bulgarian & Turkish',
    'Ungarisch, Deutsch': 'Hungarian & German',
}
