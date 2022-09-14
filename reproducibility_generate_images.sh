# generate end-to-end tables
python3 scripts/experiments/end_to_end/plot_end_to_end_table.py --mode necessary --save True && \
python3 scripts/experiments/end_to_end/plot_end_to_end_table.py --mode sufficient --save True && \

# generate end-to-end explanation length plots
python3 scripts/experiments/end_to_end/plot_explanation_lengths.py --mode necessary --model ComplEx --save True && \
python3 scripts/experiments/end_to_end/plot_explanation_lengths.py --mode necessary --model ConvE --save True && \
python3 scripts/experiments/end_to_end/plot_explanation_lengths.py --mode necessary --model TransE --save True && \
python3 scripts/experiments/end_to_end/plot_explanation_lengths.py --mode sufficient --model ComplEx --save True && \
python3 scripts/experiments/end_to_end/plot_explanation_lengths.py --mode sufficient --model ConvE --save True && \
python3 scripts/experiments/end_to_end/plot_explanation_lengths.py --mode sufficient --model TransE --save True && \

# generate end-to-end explanation length tables
python3 scripts/experiments/end_to_end/plot_explanation_lengths_table.py --mode necessary --save True && \
python3 scripts/experiments/end_to_end/plot_explanation_lengths_table.py --mode sufficient --save True && \

# generate average explanation extraction times plots
python3 /Users/andrea/kelpie/scripts/experiments/extraction_times/plot_extraction_times.py --mode necessary --save True && \
python3 /Users/andrea/kelpie/scripts/experiments/extraction_times/plot_extraction_times.py --mode sufficient --save True && \

# generate minimality experiment tables
python3 /Users/andrea/kelpie/scripts/experiments/explanation_minimality/plot_minimality_table.py --mode necessary --save True && \
python3 /Users/andrea/kelpie/scripts/experiments/explanation_minimality/plot_minimality_table.py --mode sufficient --save True && \

# generate xsi threshold comparison table
python3 /Users/andrea/kelpie/scripts/experiments/necessary_xsi_threshold/plot_xsi_threshold_comparison_table.py --save True && \

# generate prefilter k threshold comparison tables
python3 /Users/andrea/kelpie/scripts/experiments/prefilter_threshold/plot_prefilter_threshold_comparison_table.py --mode necessary --save True && \
python3 /Users/andrea/kelpie/scripts/experiments/prefilter_threshold/plot_prefilter_threshold_comparison_table.py --mode sufficient --save True && \

# generate prefilter type comparison tables
python3 /Users/andrea/kelpie/scripts/experiments/prefilter_type/plot_prefilter_type_comparison_table.py --mode necessary --save True && \
python3 /Users/andrea/kelpie/scripts/experiments/prefilter_type/plot_prefilter_type_comparison_table.py --mode sufficient --save True && \

# generate SHAP - Kelpie comparison plot
python3 /Users/andrea/kelpie/scripts/experiments/shap_kelpie_comparison/plot_shap_kelpie_comparison.py --save True && \

# generate user study plot
python3 /Users/andrea/kelpie/scripts/experiments/user_study/plot_user_study.py --save True