#!/usr/bin/env python

import argparse
import os
import sys

def get_groundtruth(gt_file):
    """
    Read a ground truth file and outputs a dictionary
    mapping queries to the set of relevant results (plus a list of all images).
    """
    gt = {}
    allnames = set()
    with open(gt_file, "r") as file:
        for line in file:
            imname = line.strip()
            allnames.add(imname)
            imno = int(imname[:-len(".jpg")])
            if imno % 100 == 0:
                gt_results = set()
                gt[imname] = gt_results
            else:
                gt_results.add(imname)

    return (allnames, gt)

def parse_results_file(fname):
    """
    Go through the results file and 
    return them in suitable structures
    """
    res = {}
    with open(fname, "r") as file:
        for line in file:
            fields = line.split()
            query_name = fields[0]
            ranks   = [int(rank) for rank in fields[1::2]]
            imnames = [im for im in fields[2::2]]
            res[query_name] = list(zip(ranks, imnames))

    return res

def compute_AP(query, gt):
    """
    Compute the average precision of one search.
    query = Ordered list of image filenames
    gt = Set with the relevant images for this query
    """
    ap = 0.0
    nrel = len(gt)
    curr_k = 1
    curr_rel = 0

    for imname in query:
        
        # Checking if the returning result is relevant to the query
        if imname in gt:
            curr_rel += 1
            ap += float(curr_rel) / float(curr_k)
        curr_k += 1

    return ap / nrel

def compute_mAP_from_file(results_file, gt_file):
    """
    Compute mAP from a file using the INRIA Holidays dataset format
    results_file = Results file following the indicated format
    gt_file = Ground truth file. Typically, 'holidays_images.dat'.
    """
    # Reading GT file
    (gt_names, gt) = get_groundtruth(gt_file)

    # Parsing results file
    results = parse_results_file(results_file)

    # Sum of AP's
    sum_ap = 0.0
    nqueries = 0

    # Processing each query
    for query_name,query_results in results.items():

        # Checking if the current query is in the dataset
        if query_name not in gt:
            print('Unknown query: %s' % query_name)
            return -1

        # Get GT for this query
        gt_results=gt.pop(query_name)

        # Sorting in ascending order
        query_results.sort()

        # Filtering the results        
        query_results_filt = []
        for _,res_name in query_results:
            #  Checking if the returned name is correct
            if res_name not in gt_names:
                print("Image name '%s' not in Holidays" % res_name)
                return -1
            
            # Checking if any of the results is the query itself
            if res_name == query_name:
                continue
            
            query_results_filt.append(res_name)      
        
        ap = compute_AP(query_results_filt, gt_results)
        sum_ap += ap
        nqueries += 1
    
    if gt:
        # Some queries left
        print("No result for queries: ", gt.keys())
        return -1
    
    return sum_ap / nqueries

def compute_mAP(results, gt_file):
    """
    Compute mAP from a resulting dictionary
    results = Dictionary containing, for each query, the ordered list of retrieved images.
              Example: {'100100.jpg': ['100101.jpg', '100102.jpg']}
    gt_file = Ground truth file. Typically, 'holidays_images.dat'.
    """
    # Reading GT file
    (gt_names, gt) = get_groundtruth(gt_file)

    # Sum of AP's
    sum_ap = 0.0
    nqueries = 0

    # Processing each query
    # for query_name,results in parse_results(results_file):
    for query_name,query_results in results.items():        

        # Checking if the current query is in the dataset
        if query_name not in gt:
            print('Unknown query: %s' % query_name)
            return -1

        # Get GT for this query
        gt_results=gt.pop(query_name)

        # Filtering the results        
        query_results_filt = []
        for res_name in query_results:
            #  Checking if the returned name is correct
            if res_name not in gt_names:
                print("Image name '%s' not in Holidays" % res_name)
                return -1
            
            # Checking if any of the results is the query itself
            if res_name == query_name:
                continue
            
            query_results_filt.append(res_name)      
        
        ap = compute_AP(query_results_filt, gt_results)
        sum_ap += ap
        nqueries += 1
    
    if gt:
        # Some queries left
        print("No result for queries: ", gt.keys())
        return -1
    
    return sum_ap / nqueries

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results_file", type=str, help="Results file")
    args = parser.parse_args()

    results_file = args.results_file

    # Testing computation of mAP from a file
    m_ap = compute_mAP_from_file(results_file, 'holidays_images.dat')
    print("mAP for %s: %.5f" % (results_file, m_ap))

    # Testing computation of mAP from a dictionary
    
    # Parsing results file
    results = parse_results_file(results_file)
    results_new = {}
    for k,v in results.items():
        l = []
        for _,img in v:
            l.append(img)
        results_new[k] = l
    
    m_ap = compute_mAP(results_new, 'holidays_images.dat')
    print("mAP for %s: %.5f" % (results_file, m_ap))
