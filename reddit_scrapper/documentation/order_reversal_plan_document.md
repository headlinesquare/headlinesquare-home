This is the function that    `order_reversal.py` should implement.

It should accept one single parameter, which is a file path with `jsonl` extended file name. For example,

```powershell
python order_reversal.py conservative_04122025_curated.jsonl
```

What `order_reversal.py` should do is described as follows.

It should open the file `conservative_04122025_curated.jsonl`, which contains JSON lines as follows:

```json
{"id": 1, "domain": "independentsentinel.com", "title": "Democrats Seethe, Go Stupid Over Trump's Iconic Photo", "url": "https://www.independentsentinel.com/democrats-seethe-go-stupid-over-trumps-iconic-photo/"}
{"id": 2, "domain": "x.com", "title": "Teen kills parents to fund plot to assassinate President Donald Trump.", "url": "https://x.com/tpantheman/status/1911176732180103447?s=46"}
{"id": 3, "domain": "hotair.com", "title": "The Left Discovers Milton Friedman", "url": "https://hotair.com/larry-elder/2025/04/12/the-left-discovers-milton-friedman-n3801700"}
......
{"id": 73, "domain": "dailywire.com", "title": "Trump’s U.S. Attorney Opens Criminal Probe Into NJ Gov For ‘Obstructing’ Immigration Enforcement", "url": "https://www.dailywire.com/news/trumps-u-s-attorney-opens-criminal-probe-into-nj-gov-for-obstructing-immigration-enforcement"}
{"id": 74, "domain": "townhall.com", "title": "Deport: Judge Makes a Decision About Pro-Terror Ring Leader", "url": "https://townhall.com/tipsheet/katiepavlich/2025/04/11/deport-judge-makes-a-decision-about-pro-terror-ring-leader-n2655411"}
```

It may contain up to 1000 JSON lines. For example, in this case, we have N = 74 lines. Each line is a news record. Each line contains "id", "domain", "title", "URL". "id" is always in the beginning, and it is numbered continuously from 1 to N.

What we want to do is to reverse the entire order of this file. The old id 1 should be the new id 74. The old id x should be the new id N+1-x. And the new file should still rank the id with ascending order. The output will be

```json
{"id": 1, "domain": "townhall.com", "title": "Deport: Judge Makes a Decision About Pro-Terror Ring Leader", "url": "https://townhall.com/tipsheet/katiepavlich/2025/04/11/deport-judge-makes-a-decision-about-pro-terror-ring-leader-n2655411"}
{"id": 2, "domain": "dailywire.com", "title": "Trump’s U.S. Attorney Opens Criminal Probe Into NJ Gov For ‘Obstructing’ Immigration Enforcement", "url": "https://www.dailywire.com/news/trumps-u-s-attorney-opens-criminal-probe-into-nj-gov-for-obstructing-immigration-enforcement"}
......
{"id": 72, "domain": "hotair.com", "title": "The Left Discovers Milton Friedman", "url": "https://hotair.com/larry-elder/2025/04/12/the-left-discovers-milton-friedman-n3801700"}
{"id": 73, "domain": "x.com", "title": "Teen kills parents to fund plot to assassinate President Donald Trump.", "url": "https://x.com/tpantheman/status/1911176732180103447?s=46"}
{"id": 74, "domain": "independentsentinel.com", "title": "Democrats Seethe, Go Stupid Over Trump's Iconic Photo", "url": "https://www.independentsentinel.com/democrats-seethe-go-stupid-over-trumps-iconic-photo/"}
```

And the output will be the same as the input file, overriding it: `conservative_04122025_curated.jsonl`.

Please carefully review the instructions, and ask questions to me if you need clarification. 
