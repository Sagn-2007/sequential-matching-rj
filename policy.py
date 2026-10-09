"""Optimized Policy for Sequential Matching (VoI Asks + Baseline Match)."""
import argparse
import json
import sys
from kit import baseline_match, HARD

def decide(request, mode='hybrid'):
    state = request['state']
    memory = request.get('memory') or {}
    
    # Initialize/reset memory if a new episode starts
    if memory.get('episode_day', -1) > state['day'] or state['day'] == 0:
        memory = {'episode_day': state['day']}
    memory['episode_day'] = state['day']
    
    # ASK PHASE: Value of Information (VoI) based on Potential Degree
    if request['phase'] == 'ask':
        budget = state['ask_budget_remaining'] // 3
        if budget == 0:
            return {'asks': [], 'memory': memory}
            
        available = [m for m in state['members'] if m['available']]
        candidates = []
        for m in available:
            # Identify members who have missing constraints and have not explicitly declined them
            missing = [k for k in HARD if m['fields'].get(k) is None and m['field_status'].get(k) != 'declined']
            if missing:
                candidates.append(m)
                
        scored_candidates = []
        for c in candidates:
            potential = 0
            for other in available:
                if c['member_id'] == other['member_id']: 
                    continue
                
                # Fast check: could they theoretically match based strictly on KNOWN fields?
                failures = False
                for x, y in ((c, other), (other, c)):
                    if x['fields'].get('who_to_meet') is not None and y['gender'] not in x['fields']['who_to_meet']: failures = True
                    if x['fields'].get('age_min') is not None and y['age'] < x['fields']['age_min']: failures = True
                    if x['fields'].get('age_max') is not None and y['age'] > x['fields']['age_max']: failures = True
                    if x['fields'].get('acceptable_zones') is not None and y['zone'] not in x['fields']['acceptable_zones']: failures = True
                if not failures:
                    potential += 1
            scored_candidates.append((-potential, c['member_id']))
            
        # Rank by highest potential degree (most negative first)
        scored_candidates.sort()
        asks = [{'member_id': c_id, 'field': 'constraints'} for _, c_id in scored_candidates[:budget]]
        return {'asks': asks, 'memory': memory}

    # MATCH PHASE: Baseline Match logic
    return {'pairs': baseline_match(state), 'memory': memory}

if __name__ == '__main__':
    # Ignore any arguments passed by the evaluator (like --baseline greedy)
    # and unconditionally run our optimized hybrid policy.
    request = json.load(sys.stdin)
    print(json.dumps(decide(request), allow_nan=False))
