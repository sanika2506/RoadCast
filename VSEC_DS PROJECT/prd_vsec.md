# RoadCast --- Product Requirements Document (PRD)

**Document type:** Product Requirements Document\
**Project:** RoadCast\
**Version:** 1.0\
**Status:** Initial requirements derived from the *RoadCast College
Project Implementation Guide* (October 2026)\
**Intended audience:** College project team, developers, data analysts,
testers, and evaluators

------------------------------------------------------------------------

## 1. Product Overview

### 1.1 Product summary

RoadCast is an educational traffic analytics application that analyzes
historical traffic measurements and presents understandable patterns in
traffic volume, speed, or congestion where the selected dataset supports
those measures. It combines data preparation, exploratory analysis,
visualizations, and optionally a simple predictive model.

RoadCast is **not** a live navigation service. Historical results must
not be represented as current traffic conditions or guaranteed travel
times.

### 1.2 Problem statement

Users need a clear way to explore historical traffic measurements for a
selected road network or geographic area and understand how traffic
varies by road, time, weekday, season, and weather when those fields are
available.

### 1.3 Product goals

1.  Load a documented public, open, or clearly labeled synthetic traffic
    dataset.
2.  Clean and prepare the data through a repeatable, documented process.
3.  Let users explore traffic patterns by the dimensions supported by
    the dataset.
4.  Present clear, correctly labeled charts that reveal recurring busy
    periods and compare available roads or segments.
5.  Provide evidence-based findings and clearly communicate data
    coverage and limitations.
6.  Optionally build and evaluate a baseline prediction model if the
    available data is suitable.
7.  Provide reproducible project materials, tests, run instructions, and
    a final report.

### 1.4 Success criteria

The project is successful when it:

-   Loads at least one suitable traffic dataset.
-   Documents the dataset source, license or reuse terms, retrieval
    date, schema, units, and time coverage.
-   Cleans data reproducibly and records important decisions and row
    counts.
-   Provides at least **three useful charts**.
-   Supports the filters applicable to the selected dataset.
-   Labels charts with units, context, and comparable time periods.
-   Reports findings that are supported by the data.
-   Clearly distinguishes observed measurements, derived categories, and
    model estimates.
-   Communicates that the data is historical rather than live.
-   Can be run and reproduced by another student using the project
    instructions.
-   If a model is included, evaluates it on held-out data against an
    appropriate baseline.

------------------------------------------------------------------------

## 2. Users and Use Cases

### 2.1 Primary users

**Student / project evaluator** - Opens the application or
demonstration. - Selects a road, segment, direction, or date range where
available. - Reviews traffic summaries and visualizations. - Understands
the findings, dataset provenance, and limitations. - Reproduces the
analysis using the supplied instructions.

**Project developer / analyst** - Selects and documents a dataset. -
Inspects and cleans records. - Builds derived time features and
visualizations. - Optionally trains and evaluates a prediction model. -
Maintains tests, analysis scripts or notebooks, and documentation.

### 2.2 Core user journey

1.  Open the RoadCast overview.
2.  Read the selected dataset and historical-data notice.
3.  Choose available filters, such as road/segment, direction, date
    range, or day type.
4.  Inspect summary indicators and charts.
5.  Review evidence-based findings for the current selection.
6.  Review the data source, coverage, units, missingness, and
    limitations.

### 2.3 Key user questions

The application should help answer questions such as:

-   Which observed road or segment has the highest traffic volume in the
    selected data?
-   At what times are recorded traffic counts typically higher?
-   How do traffic measurements vary by hour, weekday, or month?
-   How do recorded speed or congestion values change over time, if
    available?
-   Are recorded traffic measures associated with available weather or
    holiday fields?
-   If the data is suitable, can a simple baseline model estimate a
    defined traffic target?

The chosen project scope should focus on one city, region, road network,
or dataset and a manageable subset of these questions.

------------------------------------------------------------------------

## 3. Scope

### 3.1 Minimum viable product (MVP)

The MVP must:

-   Use one documented dataset for one selected geographic area, road
    network, or traffic measurement source.
-   Load and validate the data.
-   Clean the data using documented, repeatable steps.
-   Provide at least three useful charts.
-   Provide summary statistics and a few evidence-based findings.
-   Include filters appropriate to the dataset.
-   Display dataset source, coverage, units, and a historical-data
    warning.
-   Handle missing data, invalid data, empty filter results, and loading
    or processing errors clearly.
-   Include project documentation and reproducible analysis
    instructions.
-   State the assumptions and limitations of the data and results.

Machine learning is **optional** and must not block delivery of the MVP.

### 3.2 In scope

-   Historical traffic-data ingestion and preparation.
-   Exploratory data analysis and descriptive statistics.
-   Time-based analysis, such as hour, weekday, and month, when
    timestamps support it.
-   Road or segment comparisons when the dataset supports them.
-   Weather, holiday, direction, or day-type analysis when the relevant
    fields exist.
-   Interactive filters and charts.
-   Optional derived congestion categories, provided their construction
    is documented.
-   Optional prediction model with suitable evaluation.
-   Testing, documentation, reproducibility, and a local demonstration
    or optional deployment.

### 3.3 Out of scope

Unless separately approved as a future extension, RoadCast does not
require:

-   Live traffic feeds or real-time navigation.
-   Turn-by-turn directions or route optimization.
-   Guaranteed or precise travel-time estimates.
-   A complete city-wide road network when the selected dataset covers
    only a station, sample, or subset of roads.
-   Machine learning when the dataset does not support a meaningful
    target.
-   Paid hosting or paid data services.
-   User accounts, personal profiles, or user tracking.
-   Collection of personal identifiers or user interaction logs for
    traffic analysis.

### 3.4 Assumptions and constraints

-   The project is intended for a college-level educational
    demonstration.
-   The implementation technology is not prescribed by the guide; choose
    a stack appropriate to the team and document it.
-   Dataset fields, geography, date coverage, and sampling frequency
    will determine which features can be implemented.
-   Missing fields must not be replaced with invented observed values.
-   Synthetic data may be used to test an interface or algorithm, but
    must be clearly labeled and must not be used as evidence about
    actual roads.
-   Hosting is optional; a reproducible local notebook or application is
    acceptable unless course requirements say otherwise.

------------------------------------------------------------------------

## 4. Functional Requirements

Requirements below use IDs so they can be referenced in implementation
issues and test cases.

### 4.1 Dataset and provenance

**FR-01 --- Dataset selection**\
The project shall use a public/open dataset or clearly labeled synthetic
data. The chosen dataset must be suitable for the defined project
questions.

**FR-02 --- Source documentation**\
The project shall document the dataset name, owner, source URL,
retrieval/download date, license or terms, attribution requirements,
geographic coverage, time coverage, and any relevant reuse or
redistribution restrictions.

**FR-03 --- Data dictionary**\
The project shall provide a data dictionary that defines each retained
field, its meaning, type, unit, and missing-value behavior.

**FR-04 --- Raw-data preservation**\
Where permitted, the original dataset shall be preserved separately from
processed data. Processing must not silently overwrite the source copy.

**FR-05 --- Synthetic-data labeling**\
Any synthetic data used for development, testing, or demonstration shall
be visibly identified as synthetic and kept distinct from observed
traffic data.

**FR-06 --- Schema inspection**\
The ingestion process shall check row count, columns, data types,
representative records, and relevant metadata before analysis.

### 4.2 Data preparation

**FR-07 --- Standardization**\
The preparation process shall standardize column names and data types as
needed and consistently parse timestamps. Known time zones and
measurement units shall be recorded.

**FR-08 --- Missing values**\
The process shall quantify missingness and document whether missing
records or values are retained, dropped, or imputed. Missing traffic
counts shall never silently be converted to zero.

**FR-09 --- Duplicate handling**\
The process shall define a suitable record key (for example, timestamp +
segment + direction when those fields exist) before removing duplicates.

**FR-10 --- Validity checks**\
The process shall flag and investigate invalid dates, negative counts or
speeds, inconsistent units, and other out-of-range values before
excluding them.

**FR-11 --- Category normalization**\
Road, direction, weather, and other categorical labels shall be
normalized when appropriate without merging distinct roads or meanings.

**FR-12 --- Data reshaping**\
If the source stores separate columns for each hour or measurement
period, data shall be reshaped where necessary for time-series analysis,
with the transformation documented.

**FR-13 --- Derived features**\
The system may derive hour, weekday, month, holiday, or congestion
category only when the underlying fields and assumptions support the
derivation. Label definitions and thresholds shall be documented.

**FR-14 --- Cleaning audit trail**\
The project shall retain processing steps and report record counts
before and after cleaning, along with reasons for important exclusions
or transformations.

### 4.3 Dashboard and filters

**FR-15 --- Dashboard header**\
The overview shall show the RoadCast title, the selected dataset or
source, and a prominent notice that the results describe historical
data.

**FR-16 --- Dataset-aware filters**\
The dashboard shall expose filters that are supported by the selected
dataset. Suggested filters are: - Road or segment. - Direction. -
Date/time range. - Day type (for example, weekday/weekend), when
available.

Unsupported filters shall be omitted or clearly marked unavailable; the
interface shall not fabricate filter values.

**FR-17 --- Filter consistency**\
Changing a filter shall update the relevant summary indicators, charts,
and findings consistently.

**FR-18 --- Summary indicators**\
The dashboard shall show useful summary values supported by the selected
data, such as average/median traffic volume, speed when present, and the
observed busiest period. Each measure must be clearly identified and use
the correct unit.

**FR-19 --- Empty-result state**\
If the current filter combination returns no records, the dashboard
shall explain that no data matches the selection and provide a way to
adjust or reset the filters.

**FR-20 --- Error state**\
If a dataset cannot be loaded or processed, the application shall show
an understandable error message rather than silently displaying
misleading or stale results.

### 4.4 Visualizations and findings

**FR-21 --- Minimum chart set**\
The MVP shall contain at least three useful charts selected to match the
available data. A recommended set is: 1. Traffic measurement by hour or
over time. 2. Weekday/hour heatmap, if timestamps support it. 3.
Comparison of roads or segments, if multiple comparable locations exist.

Where a recommended chart is not supported by the data, use a suitable
alternative and document why.

**FR-22 --- Chart semantics**\
Every chart shall include a descriptive title, labeled axes, units,
relevant time period or selection context, and a clear indication of
whether the values represent volume, speed, congestion, or another
measure.

**FR-23 --- Appropriate chart selection**\
Use line charts for time trends, bar charts for road comparisons, and
heatmaps for hour-by-day patterns where appropriate. A map may be
included only if reliable geographic data and suitable mapping tools are
available.

**FR-24 --- Comparable comparisons**\
Comparisons shall use compatible units, road/segment definitions, and
time periods. Differences in sampling or survey coverage shall be
disclosed where they affect interpretation.

**FR-25 --- Accessible congestion cues**\
If colors indicate congestion categories, pair the colors with text
labels or symbols so color alone does not communicate the meaning.

**FR-26 --- Evidence-based findings**\
The dashboard or report shall present a small set of findings derived
from the selected data. Statements must not exceed what the data
supports and should identify relevant time periods or selections.

### 4.5 Optional prediction

**FR-27 --- Model eligibility**\
A prediction model shall be included only if the dataset supports a
meaningful target and sufficient relevant fields. The model is optional.

**FR-28 --- Target definition**\
The project shall explicitly define the prediction target and its unit,
such as numeric traffic volume or speed, or a documented congestion
class. Volume, speed, congestion, and travel time must not be treated as
interchangeable.

**FR-29 --- Baseline comparison**\
A model shall be compared with a simple baseline, such as the
training-set mean or a historical time-of-day average.

**FR-30 --- Held-out evaluation**\
Model evaluation shall use observations kept separate from training. For
time-ordered prediction, use a chronological split where possible to
prevent future data from leaking into the past.

**FR-31 --- Appropriate metrics**\
For regression, report suitable metrics such as MAE, MSE, and R-squared
where appropriate. For classification, report a confusion matrix,
precision, recall, and F1-score. Interpret results in context and
explain class imbalance where present.

**FR-32 --- Leakage and limitations**\
The project shall check for data leakage, including fields that encode
the target directly or use future measurements. It shall explain model
limitations and avoid implying that estimates are guaranteed real-world
conditions.

**FR-33 --- Model-estimate labeling**\
Predictions, if displayed, shall be visibly labeled as estimates and
kept distinct from observed historical measurements.

### 4.6 Documentation and reproducibility

**FR-34 --- README**\
The repository shall contain a README describing the project purpose,
data source, setup, dependencies, and instructions to run the analysis
and application.

**FR-35 --- Reproducible workflow**\
The project shall document how to recreate processed data and analysis
results. Dependency versions and a fixed random seed shall be recorded
when relevant.

**FR-36 --- Repository organization**\
The repository should separate raw data, processed data, analysis,
application, documentation, and tests. Folder names may vary if the
structure remains clear.

**FR-37 --- Attribution and redistribution**\
The project shall comply with dataset attribution, license, and
redistribution terms. If the dataset cannot be redistributed, provide
retrieval instructions rather than packaging it.

**FR-38 --- Privacy**\
The project shall avoid unnecessary personal information. User
interaction logs are optional and, if collected, shall be minimal and
free of names or personal identifiers.

------------------------------------------------------------------------

## 5. Data Requirements

### 5.1 Core fields

The dataset should include traffic measurements. Useful fields include
the following, depending on the source:

  -----------------------------------------------------------------------
  Field group             Examples                Requirement
  ----------------------- ----------------------- -----------------------
  Time                    Date, timestamp, hour,  Needed for time-based
                          survey period           analysis; exact field
                                                  depends on dataset

  Road identity           Road name, segment ID,  Needed for road
                          direction,              comparisons; may be
                          count-station ID        limited in a
                                                  single-station dataset

  Traffic measure         Vehicle count, volume,  At least one suitable
                          speed, congestion       traffic measurement is
                          estimate, travel-time   needed
                          observation             

  Context                 Weather, holiday,       Optional; analyze only
                          weekday/weekend, road   if present and
                          type, incident          meaningful

  Geography               Coordinates, geographic Optional; needed for
                          segment identifier      reliable map-based
                                                  features

  Interaction logs        Selected road or filter Optional and not a
                                                  traffic measurement
  -----------------------------------------------------------------------

### 5.2 Dataset selection

The guide identifies these candidate datasets. The project team must
verify current availability, terms, and fields before committing to one.

1.  **UCI Metro Interstate Traffic Volume** --- The guide describes
    48,204 hourly records for westbound I-94 near Minneapolis--St. Paul,
    covering 2012--2018, with traffic volume, time, weather, and holiday
    fields. Suitable for volume exploration, time-of-day analysis, and
    introductory regression. It represents one interstate station and
    does not provide segment-level speed. The guide identifies CC BY 4.0
    and calls for attribution.
2.  **NYC Traffic Volume Counts (Historical)** --- Historical counts at
    bridge crossings and roadways, with road/segment identifiers,
    directions, count dates, and hourly count columns. Coverage varies
    by location and year, and does not represent every day continuously.
    Suitable for comparisons across count locations and survey periods,
    not continuous live or hourly forecasting. Review metadata and NYC
    Open Data terms.
3.  **Chicago Traffic Tracker historical congestion estimates by
    segment** --- The guide describes historical segment-level data
    beginning in 2024 but notes that the City of Chicago announced in
    August 2026 that Traffic Tracker datasets were deprecated because
    the source system changed and updates could no longer be provided.
    Treat as a historical snapshot and verify availability and staleness
    before use.

**Selection guidance:** The guide recommends UCI as a straightforward
first dataset; NYC for multi-location comparisons with uneven survey
coverage; and Chicago only after verifying that the archived data is
accessible and suitable.

### 5.3 Data integrity rules

-   Never present invented values as observations.
-   Never silently convert missing traffic counts to zero.
-   Record units and time-zone assumptions.
-   Define duplicate records before deduplication.
-   Investigate invalid ranges before excluding values.
-   Document congestion-label thresholds and do not imply arbitrary
    thresholds are universal.
-   Keep synthetic data separate from real observations.
-   Record source, license, retrieval date, coverage, schema, and
    processing steps.
-   Do not scrape or call an API contrary to its terms or rate limits.

------------------------------------------------------------------------

## 6. User Interface Requirements

### 6.1 Suggested dashboard layout

1.  **Header:** RoadCast title, selected dataset, historical-data
    notice.
2.  **Filter area:** Available road/segment, direction, date range, and
    day-type filters.
3.  **Summary area:** Supported summary statistics and observed busiest
    period.
4.  **Visualization area:** Time trend, hour/day heatmap, and location
    comparison where supported.
5.  **Findings area:** Evidence-based statements for the current
    selection.
6.  **Data and limitations area:** Source, coverage dates, units,
    missingness, synthetic-data notice if applicable, and model-estimate
    warning if a model exists.

### 6.2 Interface behavior

-   Filters must reflect only values supported by the dataset.
-   Visualizations and summaries must stay consistent with the selected
    filters.
-   Empty results must be explained.
-   Load and processing failures must be surfaced clearly.
-   Historical observations and model estimates must be distinguishable.
-   The interface must not imply live traffic, guaranteed conditions, or
    exact journey times.
-   Congestion color cues must also have text or symbols.
-   A map is optional and requires reliable coordinates or an
    appropriate geographic segment identifier.

### 6.3 Accessibility and clarity

-   Use readable chart titles, axis labels, units, and legends.
-   Do not rely on color alone to convey congestion categories.
-   Use consistent terminology throughout the interface.
-   Explain whether each displayed value is a count, speed, supplied
    congestion estimate, derived category, or model prediction.

------------------------------------------------------------------------

## 7. Non-Functional Requirements

**NFR-01 --- Reproducibility**\
A student following the README in a clean environment should be able to
reproduce the analysis and run the application or demonstration.

**NFR-02 --- Data integrity**\
Raw and processed data should be separated where permitted, and
transformations should be traceable.

**NFR-03 --- Interpretability**\
Charts, metrics, and findings must be understandable to a
college-project audience and include relevant units and context.

**NFR-04 --- Honest communication**\
The product must clearly state data coverage, missingness, limitations,
and whether results are observed, derived, synthetic, or predicted.

**NFR-05 --- Privacy minimization**\
Avoid collecting personal information that is not needed for the
project.

**NFR-06 --- Portability**\
Avoid machine-specific paths. Document configuration and dependencies so
the project can run in another suitable environment.

**NFR-07 --- Cost constraint**\
The project should not require paid services. Hosting is optional and
must be checked against course rules, data terms, availability, and
cost.

**NFR-08 --- Maintainability**\
Organize code, analysis, documentation, and tests clearly. Record
important design and data decisions in the project log or design
document.

**NFR-09 --- Appropriate claims**\
Do not claim precise travel duration unless suitable journey-time
observations exist or the calculation is clearly explained.

------------------------------------------------------------------------

## 8. Testing and Evaluation Requirements

### 8.1 Data and preprocessing tests

-   Confirm source files load successfully.
-   Check expected columns, row counts, and data types.
-   Test malformed dates and numeric values.
-   Verify missing-value handling and ensure missing counts are not
    silently changed to zero.
-   Verify duplicate handling against the defined record key.
-   Compare record counts before and after cleaning and investigate
    unexpected losses.
-   Manually check derived features on sample records, including date
    boundaries.
-   Verify units, time-zone assumptions, and category normalization.

### 8.2 Dashboard tests

-   Confirm each filter updates the appropriate charts, summaries, and
    findings.
-   Confirm no-result filter combinations display a useful empty state.
-   Confirm load or processing errors are explained.
-   Verify chart titles, labels, units, and selected time periods.
-   Check that comparisons use compatible units and periods.
-   Confirm the source, coverage, and historical-data notice are
    visible.
-   Confirm synthetic values and model estimates, if present, are
    labeled correctly.

### 8.3 Model tests (only if a model is included)

-   Separate training and test observations.
-   Use chronological splitting for time-ordered data where possible.
-   Check for target leakage and future information in input features.
-   Compare the model against a simple baseline.
-   Report appropriate regression or classification metrics.
-   Explain limitations and class imbalance where relevant.

### 8.4 Reproducibility and demonstration tests

-   Ask another student to follow the README from a clean environment.
-   Test the final demonstration in a fresh session and, where feasible,
    another browser or device.
-   Record test cases, expected results, actual results, status, and
    defect resolutions.
-   Preserve the final source version, report, and test results.

------------------------------------------------------------------------

## 9. Acceptance Criteria

The MVP is ready for evaluation when all applicable criteria below pass.

  -----------------------------------------------------------------------
  ID                      Acceptance criterion    Verification
  ----------------------- ----------------------- -----------------------
  AC-01                   One clear problem       Review
                          statement,              requirements/design
                          geographic/data scope,  document
                          and project questions   
                          are documented.         

  AC-02                   A suitable public/open  Inspect data package
                          dataset is selected, or and source notes
                          synthetic data is       
                          clearly labeled.        

  AC-03                   Dataset source, owner,  Review data card/data
                          license/terms,          dictionary
                          retrieval date, schema, 
                          units, and coverage are 
                          documented.             

  AC-04                   Data loading and schema Run ingestion checks
                          checks work.            

  AC-05                   Cleaning and feature    Re-run processing
                          creation are repeatable workflow
                          and documented.         

  AC-06                   Missing values,         Review cleaning log and
                          duplicates, invalid     tests
                          values, and row-count   
                          changes are handled     
                          transparently.          

  AC-07                   At least three useful   Inspect running
                          charts are available.   application/report

  AC-08                   Charts include labels,  Visual inspection
                          units, context, and     
                          comparable windows      
                          where applicable.       

  AC-09                   Filters supported by    Functional tests
                          the dataset update      
                          relevant outputs        
                          correctly.              

  AC-10                   Empty results and       Test empty and
                          data-loading errors are invalid-input scenarios
                          handled clearly.        

  AC-11                   Volume, speed,          Review labels,
                          congestion, and travel  definitions, and claims
                          time are not confused.  

  AC-12                   Historical observations Inspect interface
                          are clearly             
                          distinguished from      
                          predictions;            
                          historical-data notice  
                          is visible.             

  AC-13                   Findings are supported  Review report and
                          by the selected data    findings
                          and limitations are     
                          documented.             

  AC-14                   If a model is included, Review model evaluation
                          it uses held-out        
                          evaluation, a suitable  
                          baseline, and           
                          appropriate metrics.    

  AC-15                   Another student can     Clean-environment
                          follow the README to    reproduction test
                          reproduce the work.     

  AC-16                   Repository, report,     Final project audit
                          tests, and data         
                          handling comply with    
                          source terms and avoid  
                          credentials/private     
                          files.                  
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 10. Deliverables

The project should provide the following artifacts, matching the
implementation guide.

  -----------------------------------------------------------------------
  Deliverable             Suggested format        Required contents
  ----------------------- ----------------------- -----------------------
  Requirements and design Markdown or PDF         Problem, objectives,
                                                  scope, user flow,
                                                  wireframes,
                                                  architecture, data
                                                  plan, acceptance checks

  Source repository       Git repository + README Source code,
                                                  dependencies, run
                                                  instructions,
                                                  attribution, version
                                                  history

  Data package or data    CSV/JSON if             Source, license,
  card                    redistribution is       retrieval date, schema,
                          permitted; otherwise    units, coverage,
                          Markdown                retrieval instructions

  Analysis                Notebook and/or scripts Loading, cleaning,
                                                  exploration, charts,
                                                  and modeling/evaluation
                                                  if used

  Application/demo        Source files + run      Filters,
                          guide; hosted URL       visualizations, empty
                          optional                states, source and
                                                  limitation notice

  Test plan and results   Markdown, CSV, or       Test cases,
                          spreadsheet             expected/actual
                                                  results, status, fixes

  Final report            PDF plus editable       Methods, findings,
                          source                  evaluation,
                                                  limitations,
                                                  screenshots, references

  Presentation evidence   Slides/PDF/recording    Project question, data,
  (if required)                                   workflow, results,
                                                  limitations
  -----------------------------------------------------------------------

### 10.1 Final report outline

1.  Title page and course/team details.
2.  Problem statement and objectives.
3.  Scope and assumptions.
4.  Dataset source, license, schema, units, and coverage.
5.  Preprocessing and data-quality results.
6.  Exploratory analysis and visualizations.
7.  Model and baseline, if used.
8.  Evaluation method and results, if applicable.
9.  Application design and screenshots.
10. Findings and interpretation.
11. Limitations, ethics, and future work.
12. Conclusion.
13. References and dataset attribution.
14. Appendix: tests, data dictionary, and run instructions.

------------------------------------------------------------------------

## 11. Implementation Plan

Follow these phases in order and record important decisions.

### Phase 1 --- Requirements gathering

-   Define one-sentence problem statement.
-   Choose project questions and geographic/data scope.
-   Map planned outputs to required data fields.
-   Define acceptance checks.
-   Record licensing, privacy, and ethical considerations.

### Phase 2 --- Dataset selection and data plan

-   Review candidate datasets and select one matching the project
    questions.
-   Verify availability, source, license, terms, and redistribution
    rules.
-   Inspect fields, geography, frequency, coverage, and missingness.
-   Define the unit of analysis.
-   Create the data dictionary and preserve a raw copy where permitted.

### Phase 3 --- Design

-   Sketch the flow: overview → choose road/segment → choose time range
    → inspect results.
-   Plan filters, summary indicators, charts, findings, and source
    notes.
-   Choose chart types based on the fields available.
-   Define empty-data and error states.
-   Prepare architecture and wireframe diagrams if required.

### Phase 4 --- Development and analysis

-   Create a clearly organized repository and README.
-   Load and validate the data.
-   Clean and document transformations.
-   Create justified features.
-   Explore distributions and summary statistics.
-   Build and verify charts and filters.
-   Add a baseline model only if appropriate.
-   Save steps/settings required to reproduce results.

### Phase 5 --- Testing and evaluation

-   Test data loading, cleaning, derived features, filters, empty
    states, and chart semantics.
-   Compare row counts before and after cleaning.
-   Evaluate a model using held-out data and a baseline if a model
    exists.
-   Check for leakage and explain limitations.
-   Record test results and defect resolutions.
-   Have another student follow the README from a clean environment.

### Phase 6 --- Deployment or demonstration

-   Decide whether hosting is needed; local execution is acceptable
    unless course rules require otherwise.
-   Remove machine-specific paths and document configuration.
-   Record dependency versions or an environment file.
-   Respect data redistribution terms.
-   Test the final demo in a fresh session.
-   Ensure source, coverage dates, units, and the historical-data notice
    are visible.
-   Preserve final source, report, and test results.

------------------------------------------------------------------------

## 12. Risks, Limitations, and Mitigations

  -----------------------------------------------------------------------
  Risk or limitation                  Mitigation
  ----------------------------------- -----------------------------------
  Dataset covers only one station or  State coverage explicitly; do not
  selected survey periods             imply city-wide or continuous
                                      coverage

  Missing or inconsistent records     Quantify missingness, document
                                      cleaning, and test the resulting
                                      dataset

  Dataset availability or terms       Record retrieval date and verify
  change                              terms before use or redistribution

  Synthetic data is mistaken for real Label it prominently and separate
  traffic                             it from observed data

  Inappropriate comparisons across    Compare compatible units and time
  roads or periods                    windows; disclose sampling
                                      differences

  Congestion labels are arbitrary     Document their source and
                                      thresholds; do not present them as
                                      universal

  Prediction model leaks future       Use held-out data and chronological
  information                         splits where appropriate; audit
                                      features

  Model estimates are interpreted as  Label predictions as estimates and
  certainty                           report metrics and limitations

  Product is mistaken for live        Show a persistent historical-data
  navigation                          notice and avoid live-condition
                                      claims

  Deployment incurs cost or violates  Keep hosting optional and verify
  terms                               course, dataset, and hosting
                                      constraints
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 13. Decisions Still to Be Confirmed

The implementation guide intentionally leaves some project-specific
choices open. The team should resolve and record these before or during
design:

-   [ ] Selected dataset and its verified source URL.
-   [ ] Geographic area, road network, or measurement station covered.
-   [ ] Dataset license, attribution, redistribution conditions, and
    retrieval date.
-   [ ] Actual fields, units, time zone, and time coverage in the chosen
    data.
-   [ ] Final project questions and the three or more charts to
    implement.
-   [ ] Technology stack and execution environment.
-   [ ] Whether prediction is justified by the available data.
-   [ ] If prediction is included, target definition, baseline, split
    strategy, and metrics.
-   [ ] Whether the project will run locally only or be hosted.
-   [ ] Any additional requirements imposed by the course or instructor.

These items are not assumed to be decided by this PRD. Do not implement
unsupported features until the selected data and project constraints are
confirmed.

------------------------------------------------------------------------

## 14. References

This PRD is based primarily on the following supplied source:

-   *RoadCast College Project Implementation Guide*, prepared by Manus
    AI, October 2026, especially sections on project overview,
    implementation phases, data requirements, preprocessing,
    analysis/interface, deliverables, and completion checklist.

The guide lists these dataset references for verification during dataset
selection:

1.  UCI Machine Learning Repository --- Metro Interstate Traffic Volume.
2.  NYC Open Data --- Traffic Volume Counts (Historical).
3.  NYC Open Data --- Traffic Volume Counts (Historical) metadata.
4.  Data.gov --- Chicago Traffic Tracker: Historical Congestion
    Estimates by Segment.
5.  Chicago Data Portal --- Traffic Tracker datasets status notice.

The final project must add the actual dataset URL, retrieval date,
license/terms, and any required attribution after the dataset is
selected and verified.
