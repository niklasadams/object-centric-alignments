from algorithm import calculate_oc_alignments
from localocpa.objects.log.importer.ocel import factory as ocel_import_factory_json
import helperfunctions
import timeit
import tracemalloc
from test_ocpns import TestOCPNS
from visualization import alignment_viz
import matplotlib.pyplot as plt
from tqdm import tqdm
import localocpa.algo.util.filtering.log.case_filtering as case_filtering


ocel_filename = "filtered_BPI2017.jsonocel"
ocel = ocel_import_factory_json.apply(ocel_filename)

ocpn = TestOCPNS().loan_application_de_jure()
x = []
y_time = []
y_memory = []
for i in tqdm(range(0,len(ocel.variants))):

    v = ocel.variants[i]

    corresponding_pexec = ocel.variants_dict[v][0]

    pexec_events = ocel.process_executions[corresponding_pexec]

    # Filtering the event log according to the one process execution
    var_ocel = case_filtering.filter_process_executions(ocel,[pexec_events])

    number_of_events = len(var_ocel.log.log)
    number_of_variants = len(var_ocel.variants)
    if number_of_variants != 1:
        print("Variant filtering resulted in more than 1 variant!")

    pexec_objects =  var_ocel.process_execution_objects[0]

    number_of_objects = len(pexec_objects)
    object_dict = {ot: len([o for (t,o) in pexec_objects if t == ot]) for ot in set([t for (t,_) in pexec_objects])}
    number_of_offers = object_dict["offer"]

    # We skip large number of offers because they are extremely slow and rare, leading to unreliable results
    if number_of_offers > 7:
        continue



    # Repetition
    n = 1
    do_memory = True
    do_time = True

    # Time analysis
    if do_time:
        t = timeit.Timer(lambda:  calculate_oc_alignments(var_ocel, ocpn))
        result = t.timeit(n)

    # Memory analysis
    if do_memory:
        tracemalloc.start()

        resulting_alignment = calculate_oc_alignments(var_ocel, ocpn)

        snapshot = tracemalloc.take_snapshot()



    if do_memory:
        alignment_cost_total = 0
        alignment_count = 0
        for variant_id, alignment in resulting_alignment.items():
            alignment_count += 1
            alignment_cost_total += len(var_ocel.variants_dict[variant_id]) * alignment.get_cost()


    if do_memory:

        # if alignment exist then visualize it
        abbreviations = {
            "Create application": "CA",
            "Submit": "Submit",
            "Create offer": "CO",
            "Call": "Call",
            "Accept offer": "AO",
            "Cancel offer": "CanO"
        }
        ot_counter = {"application":1,"offer":1}
        for (ot,o) in pexec_objects:
            abbreviations[o] = ot + str(ot_counter[ot])
            ot_counter[ot]+=1
        vis_plot = alignment_viz(next(iter(resulting_alignment.values())), abbreviations)
        vis_plot.savefig("visualization/visualization_variant_"+str(i)+".pdf")
        plt.close()
        y_time.append(result / n)
        y_memory.append(helperfunctions.get_mem_total(snapshot))

        # save information to file
        f = open("thesis_evaluation_results_7.csv", "a")
        f.write(f"{number_of_events};{number_of_objects};{number_of_offers};{alignment_cost_total};{alignment_count};{result / n};{helperfunctions.get_mem_total(snapshot)}\n")
        f.close()

