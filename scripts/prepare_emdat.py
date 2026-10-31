import csv, json, re, collections, datetime
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'data' / 'source' / 'EM-DAT Custom Request Oct 31 2026.xlsx'
OUT = ROOT / 'data' / 'processed'
wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
ws = wb['EM-DAT Data']; ws.reset_dimensions()
rows = ws.iter_rows(values_only=True)
headers = list(next(rows)); records = []
for vals in rows:
    records.append(dict(zip(headers, vals)))

def event_id(disno):
    parts = str(disno).split('-')
    return '-'.join(parts[:2]) if len(parts) >= 3 else str(disno)
def valid_date(y,m,d):
    if y is None or m is None or d is None: return ''
    try: return datetime.date(int(y),int(m),int(d)).isoformat()
    except (ValueError,TypeError,OverflowError): return ''
def blank(v): return v is None or v == ''
def num(v):
    if blank(v): return None
    if isinstance(v,(int,float)): return v
    try: return float(v)
    except (ValueError,TypeError): return None

def derive(r):
    y = num(r['Start Year'])
    return {
      'Event ID': event_id(r['DisNo.']),
      'Start Date': valid_date(r['Start Year'],r['Start Month'],r['Start Day']),
      'End Date': valid_date(r['End Year'],r['End Month'],r['End Day']),
      'Decade': (int(y)//10)*10 if y is not None else '',
      'Has Coordinates': 'Yes' if num(r['Latitude']) is not None and num(r['Longitude']) is not None else 'No',
      "Total Damage, Adjusted (million US$)": (num(r["Total Damage, Adjusted ('000 US$)"])/1000 if num(r["Total Damage, Adjusted ('000 US$)"]) is not None else None),
    }

natural = [r for r in records if r['Disaster Group'] == 'Natural']
add_fields = ['Event ID','Start Date','End Date','Decade','Has Coordinates',"Total Damage, Adjusted (million US$)"]
clean_headers = headers + add_fields
for r in natural: r.update(derive(r))

def write_csv(name, fields, data):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(data)
write_csv('cleaned_natural_disaster_impacts.csv', clean_headers, natural)

by_event=collections.defaultdict(list)
for r in natural: by_event[r['Event ID']].append(r)
metric_fields=['Total Deaths','No. Injured','No. Affected','No. Homeless','Total Affected',"Total Damage, Adjusted ('000 US$)","Total Damage, Adjusted (million US$)",'Magnitude']
events=[]
for eid, rs in by_event.items():
    first=rs[0]
    out={k:first.get(k) for k in ['Event ID','Disaster Group','Disaster Subgroup','Disaster Type','Disaster Subtype','Classification Key','Start Year','Start Month','Start Day','Start Date','End Year','End Month','End Day','End Date','Decade']}
    out['Country Count']=len({r['ISO'] for r in rs}); out['Countries']=' | '.join(sorted({str(r['Country']) for r in rs if r['Country']})); out['ISO Codes']=' | '.join(sorted({str(r['ISO']) for r in rs if r['ISO']})); out['Country Impact Records']=len(rs)
    for m in metric_fields:
        vv=[num(r.get(m)) for r in rs if num(r.get(m)) is not None]
        out[m]=sum(vv) if vv else None
        out[m+' Reported Country Impacts']=len(vv)
    events.append(out)
event_fields=list(events[0].keys())
write_csv('natural_disaster_events.csv',event_fields,events)

# Type-level frequency counts unique events; summed impact amounts roll up all country-impact rows.
type_map=collections.defaultdict(list)
for e in events: type_map[e['Disaster Type']].append(e)
types=[]
for t, es in sorted(type_map.items()):
    out={'Disaster Group':'Natural','Disaster Type':t,'Unique Events':len(es)}
    for m in metric_fields:
        vv=[num(e.get(m)) for e in es if num(e.get(m)) is not None]
        out[m]=sum(vv) if vv else None
        out[m+' Events with Reported Values']=sum(1 for e in es if num(e.get(m)) is not None)
    types.append(out)
write_csv('natural_disaster_type_summary.csv',list(types[0].keys()),types)

# Country-year-type summaries from impacts; event count uses unique core Event IDs.
cy=collections.defaultdict(list)
for r in natural: cy[(r['ISO'],r['Country'],r['Region'],r['Subregion'],r['Start Year'],r['Disaster Type'])].append(r)
cyout=[]
for (iso,country,region,subregion,year,typ), rs in sorted(cy.items(),key=lambda x:(str(x[0][4]),str(x[0][2]),str(x[0][1]),str(x[0][5]))):
    out={'ISO':iso,'Country':country,'Region':region,'Subregion':subregion,'Start Year':year,'Decade':(int(year)//10)*10 if year else None,'Disaster Type':typ,'Country Impact Records':len(rs),'Unique Events':len({r['Event ID'] for r in rs})}
    for m in metric_fields:
        vv=[num(r.get(m)) for r in rs if num(r.get(m)) is not None]
        out[m]=sum(vv) if vv else None
        out[m+' Reported Records']=len(vv)
    cyout.append(out)
write_csv('natural_country_year_type_summary.csv',list(cyout[0].keys()),cyout)

# concise QA summary for handover
metrics=['Total Deaths','Total Affected',"Total Damage, Adjusted ('000 US$)",'Magnitude']
missing={m:sum(blank(r.get(m)) for r in natural) for m in metrics}
coords=sum(derive(r)['Has Coordinates']=='Yes' for r in natural)
monthday_missing=sum(blank(r.get('Start Month')) or blank(r.get('Start Day')) for r in natural)
invalid_dates=sum(bool(r.get('Start Month')) and bool(r.get('Start Day')) and not valid_date(r.get('Start Year'),r.get('Start Month'),r.get('Start Day')) for r in natural)
print(json.dumps({'source_rows':len(records),'natural_impacts':len(natural),'natural_events':len(events),'types':len(types),'country_year_type_groups':len(cyout),'multi_country_events':sum(e['Country Count']>1 for e in events),'coords':coords,'missing':missing,'incomplete_start_dates':monthday_missing,'invalid_complete_start_dates':invalid_dates,'min_year':min(int(r['Start Year']) for r in natural if r['Start Year'] is not None),'max_year':max(int(r['Start Year']) for r in natural if r['Start Year'] is not None)},indent=2))
