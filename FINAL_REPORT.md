# Final Report

## What Makes a Developer Earn More?  
### The Role of Language Popularity and Structural Factors in Salary Formation

**Course:** DSA210 Introduction to Data Science  
**Student:** Nil Kadakal  
**Project Repository:** https://github.com/NilKadakal/DSA210_NilKadakal  
**Interactive Website:** https://nilkadakal.github.io/DSA210_NilKadakal/website/

---

## 1. Motivation

The main motivation behind this project is to understand which factors are associated with higher developer salaries in the software industry. As a Computer Science and Engineering student, I am personally interested in how technical skills, programming language choices, work conditions, and experience levels shape career outcomes. In technology-related career discussions, programming languages are often treated as direct indicators of market value. For example, it is common to hear claims such as “learning a popular language leads to a better salary” or “some languages are automatically more valuable than others.” However, salary formation is likely more complex than language choice alone.

This project therefore investigates whether programming language popularity has a meaningful relationship with developer compensation after considering broader labor-market and professional factors. The research question guiding the project is:

**To what extent do programming language choice and market popularity influence developer salaries after controlling for structural variables such as experience, education, country, and work modality?**

The original hypothesis was that programming language choice, years of professional experience, education level, and work modality would significantly explain salary differences. At the same time, I expected programming language popularity, measured through the TIOBE index, to have a positive but limited marginal effect on salary formation. In other words, I did not expect popularity alone to dominate compensation outcomes, but I expected it to add some explanatory value when combined with other variables.

This project is also personally relevant because it connects data science methodology with career planning. Instead of relying on general assumptions about which skills are valuable, the project uses real developer survey data, statistical tests, and machine learning models to examine the issue empirically.

---

## 2. Data Source and Collection

The main dataset used in this project is the **Stack Overflow Developer Survey 2024**. This dataset contains developer-level responses on salary, programming languages, years of coding experience, professional experience, country, education level, employment status, developer role, work modality, and organization size. It is suitable for this project because it combines both technical skill variables and structural career-related variables.

Since the project uses a publicly available dataset, it was enriched with an additional external dataset: the **TIOBE Index 2024**. The TIOBE index was used as a proxy for programming language popularity. Monthly TIOBE ratings were collected and processed into yearly average popularity scores for programming languages. These yearly language popularity scores were then merged with the Stack Overflow Developer Survey data based on programming language names.

The data preparation process included the following steps:

1. Loading the Stack Overflow Developer Survey 2024 dataset.
2. Selecting relevant columns related to salary, experience, country, work modality, education, developer type, organization size, and programming languages.
3. Filtering respondents with valid yearly compensation values.
4. Removing missing or invalid salary observations.
5. Removing extreme salary outliers to reduce distortion from unrealistic or highly unusual values.
6. Converting experience variables into numeric form.
7. Applying a log transformation to salary because compensation values were strongly right-skewed.
8. Splitting multi-language responses into language-level rows.
9. Merging language-level rows with TIOBE yearly average popularity ratings.
10. Saving processed datasets, result tables, and generated figures under the project repository structure.

Due to GitHub file size limitations, sampled versions of the processed datasets are included in the repository. The full datasets are made available externally through the Google Drive link documented in the README.

---

## 3. Data Analysis

The project followed the main stages of the data science pipeline: data cleaning, preprocessing, exploratory data analysis, hypothesis testing, machine learning modeling, interpretation, and presentation through an interactive website.

### 3.1 Data Cleaning and Preprocessing

The original survey data required several preprocessing steps before analysis. Salary values were cleaned by removing missing entries and filtering extreme outliers. Since salary data tends to be highly right-skewed, raw compensation values were transformed using a logarithmic transformation. This made the target variable more stable for both statistical testing and machine learning models.

Experience variables also required cleaning. In the survey, values such as “Less than 1 year” or “More than 50 years” are not directly usable as numeric variables. These responses were converted into approximate numeric values so that experience could be used in statistical analysis and model training.

Categorical variables such as country, education level, remote work status, developer type, and organization size were preserved for interpretation and later encoded for machine learning. Programming language responses were handled as multi-label data because a single developer can report using multiple languages. To connect each language with TIOBE popularity, the dataset was expanded into language-level rows.

### 3.2 Exploratory Data Analysis

The exploratory data analysis focused on understanding salary patterns across developer characteristics and programming languages. The main EDA areas were:

- Salary distribution
- Salary by years of experience
- Salary by work modality
- Salary by programming language
- Relationship between TIOBE language popularity and median salary

The salary distribution showed a strong right skew. Most developers were concentrated in a lower or moderate salary range, while a smaller number of respondents reported very high compensation. This supported the decision to use log-transformed salary in later stages.

The experience analysis showed that salary generally increases with both total coding experience and professional coding experience. However, salary variation remained large even within similar experience levels. This suggested that experience matters, but it does not fully explain salary differences by itself.

The work modality analysis showed that remote and in-person developers had different salary patterns. This supported the idea that work modality is associated with compensation. However, this result requires careful interpretation because remote work can also be related to country, job seniority, company type, and access to international labor markets.

The language-based analysis showed that salaries differ across programming languages. Some languages were associated with higher median salaries, while others were more common but not necessarily linked to higher compensation. This distinction became important when comparing programming language popularity with salary outcomes.

### 3.3 Hypothesis Testing

Three statistical tests were used to evaluate the main relationships observed during EDA.

#### ANOVA: Salary Differences Across Programming Languages

A one-way ANOVA test was used to evaluate whether mean log salaries differed significantly across programming languages. The result was statistically significant, with a very small p-value. This indicates that salary differences across programming language groups are unlikely to be explained by random variation alone. Therefore, programming language choice is associated with salary differences.

#### Welch t-test: Remote vs In-Person Work

A Welch two-sample t-test was used to compare log salaries between remote and in-person developers. The result was statistically significant. This suggests that salary differs meaningfully between remote and in-person work categories. However, this does not prove that remote work itself causes higher salary. Instead, remote work may be connected to broader structural factors such as country, role type, seniority, and international job access.

#### Spearman Correlation: TIOBE Popularity vs Median Salary

A Spearman correlation test was used to examine whether programming language popularity is associated with median salary by language. The result was not statistically significant. The correlation coefficient was approximately negative and the p-value was above the usual significance threshold. This means that the analysis did not find strong evidence of a monotonic relationship between TIOBE popularity and median developer salary.

This result was one of the most important findings of the project. It suggests that a language being popular does not necessarily mean that it is associated with higher compensation.

### 3.4 Machine Learning Analysis

For the machine learning component, the project compared baseline models with extended models that include programming language and TIOBE popularity features. The target variable was **log-transformed yearly compensation**.

The models were evaluated using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² score

The following models were trained:

1. Baseline Ridge Regression
2. Baseline Random Forest Regressor
3. Extended Ridge Regression with TIOBE features
4. Extended Random Forest Regressor with TIOBE features

The baseline models used structural and demographic variables such as country, years of coding experience, years of professional coding experience, age group, work modality, education level, developer type, and organization size. The extended models added programming language, average TIOBE rating, and the number of months observed in the TIOBE index.

Because the dataset was expanded by programming language, the same respondent could appear in multiple rows. To prevent data leakage, the train-test split was performed using `ResponseId` as a grouping variable. This ensured that the same developer did not appear in both the training and testing sets.

The model comparison results were:

| Model | MAE log | RMSE log | R² log | MAE USD | RMSE USD |
|---|---:|---:|---:|---:|---:|
| Extended Ridge Regression + TIOBE | 0.554 | 0.875 | 0.481 | 29,946 | 46,477 |
| Baseline Ridge Regression | 0.555 | 0.879 | 0.476 | 29,989 | 46,420 |
| Baseline Random Forest | 0.565 | 0.883 | 0.472 | 30,235 | 45,899 |
| Extended Random Forest + TIOBE | 0.566 | 0.884 | 0.470 | 30,207 | 46,080 |

The best-performing model was **Extended Ridge Regression + TIOBE**, with an R² score of 0.481. The baseline Ridge Regression model had an R² score of 0.476. Therefore, adding programming language and TIOBE popularity features improved the Ridge model slightly, but the improvement was small.

The Random Forest models did not outperform Ridge Regression. This suggests that a more complex nonlinear model did not necessarily provide better predictive performance for this dataset. A possible explanation is that salary is shaped more by broad structural variables, especially country and experience, than by nonlinear interactions among language-related features.

The Random Forest feature importance results also supported this interpretation. The most important predictors were:

- Country: United States
- Years of coding experience
- Years of professional coding experience
- Country-related categories
- Average TIOBE Rating
- Age group
- Remote work status

Average TIOBE Rating appeared among the top features, but its importance was much lower than country and experience-related variables. This supports the conclusion that language popularity contributes some information, but it is not the primary driver of salary prediction.

### 3.5 Interactive Project Website

As additional presentation material, an interactive project website was created and deployed using GitHub Pages:

**Website:** https://nilkadakal.github.io/DSA210_NilKadakal/website/

The website summarizes the main findings in a more visual and accessible way. It includes:

- The main project conclusion
- The best-performing machine learning model
- Baseline vs extended model comparison
- Random Forest feature importance results
- Key findings from EDA, hypothesis testing, and machine learning
- A scenario-based salary estimator

The salary estimator should not be interpreted as an exact salary prediction system. Instead, it is a transparent what-if interface calibrated to the project findings. It reflects the main conclusion that country and experience have stronger effects on salary prediction than programming language popularity alone.

---

## 4. Findings

The project produced several key findings.

First, programming language choice is associated with salary differences. The ANOVA test showed statistically significant salary differences across programming languages. This means that the technical tools developers use are related to compensation outcomes.

Second, work modality is associated with salary. The Welch t-test showed a significant difference between remote and in-person developers. However, this result should be interpreted carefully because work modality may be connected to other structural factors such as country, seniority, and access to international companies.

Third, programming language popularity is not a strong standalone predictor of salary. The Spearman correlation test between TIOBE popularity and median salary was not statistically significant. This suggests that popularity and compensation are not the same concept. A programming language can be widely used without necessarily being associated with higher salaries.

Fourth, machine learning results showed that adding TIOBE features provides only a small improvement. The Extended Ridge Regression model improved R² from 0.476 to 0.481 compared with the baseline Ridge model. This supports the original hypothesis that language popularity has a limited marginal effect.

Fifth, structural factors dominate salary prediction. Random Forest feature importance showed that country, especially being located in the United States, and years of experience were much stronger predictors than TIOBE popularity. This suggests that salary formation depends more on labor-market context and professional background than on language popularity alone.

Overall, the results partially support the original hypothesis. Programming language choice, experience, and work modality are meaningful factors in salary formation. However, programming language popularity has only a limited effect after broader structural variables are considered.

---

## 5. Personal Observations

One of my main observations during the project was that salary prediction is much more complex than it appears at first. At the beginning, I expected programming language popularity to have a clearer relationship with compensation. However, the analysis showed that popularity does not directly translate into higher salary.

A language can be popular because it is used widely in many general-purpose or entry-level contexts. This does not automatically make it highly paid. On the other hand, a less popular language may be connected to specialized industries, senior roles, or narrower but higher-paying domains. Therefore, market popularity and market value should not be treated as identical concepts.

Another important observation was the strength of country-level effects. The feature importance results showed that geography was one of the most powerful predictors of salary. This made it clear that compensation is not only about individual technical skills. It is also shaped by the economic and labor-market environment in which a developer works.

I also observed that model complexity does not guarantee better performance. Random Forest is more flexible than Ridge Regression, but it did not perform better in this project. This helped me understand that simpler models can sometimes be more effective when the strongest signals in the data are broad structural factors.

Finally, I learned that interpretation is as important as prediction. The goal of this project was not only to estimate salaries, but also to understand which factors matter. Combining EDA, hypothesis testing, machine learning, and feature importance analysis produced a stronger explanation than using only one method.

---

## 6. Limitations and Future Work

This project has several limitations.

First, the Stack Overflow Developer Survey is self-reported. Salary, experience, job role, and other variables may contain reporting errors or inconsistencies. Respondents may estimate compensation differently depending on bonuses, currency conversion, tax systems, and employment conditions.

Second, the dataset is cross-sectional. It captures respondents at a single point in time, so the project cannot establish causal relationships. For example, although remote work is associated with salary differences, the analysis cannot prove that remote work causes higher compensation.

Third, country effects are very strong, but the project does not fully adjust for cost of living, taxation, purchasing power, or local labor-market conditions. A salary that appears high in one country may not represent the same real purchasing power as a lower salary in another country.

Fourth, TIOBE is only one measure of programming language popularity. While it is useful as an external enrichment source, it may not perfectly represent labor-market demand, job posting volume, or salary premiums. Other indicators such as GitHub repository activity, Stack Overflow tag activity, LinkedIn job postings, or job advertisement datasets could provide additional perspectives.

Fifth, programming language use is complex. Many developers use multiple languages, and salary may depend more on domain specialization, seniority, role type, industry, and company characteristics than on any single language. Future work could analyze specific developer categories separately, such as backend developers, frontend developers, data scientists, DevOps engineers, embedded developers, and engineering managers.

Future extensions could include:

- Adding cost-of-living and purchasing power adjustments by country
- Comparing multiple years of Stack Overflow survey data
- Using job posting datasets to measure actual labor-market demand
- Testing additional models such as Gradient Boosting or XGBoost
- Building separate models for different developer roles
- Exploring interaction effects between country, experience, remote work, and language choice
- Improving the interactive website with charts generated directly from output files
- Creating a more advanced dashboard with filters for country, role, and experience level

---

## 7. Conclusion

This project investigated whether programming language popularity and structural factors explain developer salaries. The results show that programming language choice and work modality are associated with salary differences, but language popularity alone is not a strong predictor of compensation.

The machine learning results further support this conclusion. Adding TIOBE popularity features slightly improved the Ridge Regression model, but the improvement was small. The strongest predictors were country and experience, indicating that salary formation is shaped primarily by structural labor-market factors.

The final conclusion is that developers should not interpret programming language popularity as a direct salary signal. Popularity may reflect broad usage, but salary formation depends more heavily on geography, experience, work conditions, specialization, and broader market context. This provides a more realistic and data-driven perspective on career planning in software development.

---

## 8. Project Materials

- GitHub Repository: https://github.com/NilKadakal/DSA210_NilKadakal
- Interactive Project Website: https://nilkadakal.github.io/DSA210_NilKadakal/website/
- Main EDA and Hypothesis Testing Notebook: `Developer_Salary_Analysis.ipynb`
- Machine Learning Notebook: `ml_salary_models.ipynb`
- Website Source File: `website/index.html`
- ML Output Tables: `outputs/tables/`
- Generated Figures: `outputs/figures/`

---

## 9. AI Assistance Disclosure

AI tools were used for writing assistance, debugging support, structuring explanations, improving the clarity of markdown documentation, and refining the presentation of the final report and website text. All analysis decisions, code execution, result interpretation, repository organization, and final submission were reviewed and completed by the author.
