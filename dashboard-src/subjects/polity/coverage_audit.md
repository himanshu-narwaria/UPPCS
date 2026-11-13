# Indian Polity: source coverage and learning audit

Audit date: 13 November 2026.

The supplied PDF has 530 file pages. The active study files now provide 42 readable chapter guides, four complete points per guide, comparisons, a confusion check and 126 hidden-answer recall prompts. The full notes retain the extracted chapter openings and all 2,788 source question/explanation cards behind closed evidence panels.

Practice contains 1,213 scorable UPPSC-labelled questions. A further 57 UPPSC items retain a printed asterisk or malformed options and remain explicitly unscored: 1,270 UPPSC source items in total. Four options are present on every scored item. All-exam evidence can have five options. There are 142 repeated UPPSC items; counts use distinct printed exam labels, not estimates or other exams.

## What the cross-check establishes

- All 42 source chapter headings were located in visual column order. The correct starts include Articles on file page 41, Governance System on 69, and State Legislature on 331.
- Every printed answer marker in the unique chapter stream has a retained source record. Reconstructing each chapter from its opening, raw question bodies, keys, explanations and printed cross-references leaves zero missing normalized word-token counts in all 42 chapters.
- Independent pypdf stream extraction and PDFium column extraction have zero missing cleaned a-z/0-9 character counts on all 524 content pages. This check ignores order, spaces and punctuation; it detects omitted character content, not incorrect meaning.
- Four duplicate PDF page pairs are retained in the original file and deduplicated in the study stream: 31/32, 69/70, 136/137, 410/411.
- Questions preserve their actual printed options and keys. No True/False questions, default A keys, invented years, or cut-off explanations are added. Matching-list questions use the final answer-code option run. Printed 'see above' references retain their original text and the resolved explanation/page provenance.
- Chapter 1 restarts printed numbering after its historical subsection. Q113 about BHARATPOL in Miscellaneous and Q44 in Supreme Court have their complete stems. These cases are checked by the validator.

## Important source error

The source's chapter 41 labels women's Lok Sabha reservation as Article 300 A. The learning layer corrects this to Article 330A and explains that Article 300A concerns property. Primary Legislative Department PDFs were checked on 13 November 2026:

- [Women's representation: Article 330A](https://www.legislative.gov.in/static/uploads/2025/08/cb1b190ea633a1746368ed1fac35fb30.pdf)
- [Constitution: Article 300A and property](https://www.legislative.gov.in/static/uploads/2025/07/359f70a69695affb9d72f8393102bd2e.pdf)

The Federal Court question on PDF page 11 prints options for 1861, 1909 and 1919, then None of the above. Its book key (d) is consistent with its explanation of the Government of India Act, 1935; it must not be rewritten as option C or 1905.

## Limits and verification

This is a full structural retention audit plus selective teaching synthesis. It does not establish that every explanation, legal proposition, statistic, office-holder or original exam key is correct. Source-era claims stay explicitly labelled. The book's keys are not described as independently verified official keys. The guide is selective; additional important detail remains in the evidence panels and original PDF.

Static checks validate data provenance, scored/review separation, chapter and repeat totals, all local anchors, complete 72-hour scheduling, distinct multipart reading/questions, four disjoint 25-question practice mocks, embedded JavaScript syntax, and absence of inline event attributes or external loaded resources. Live browser visual/interaction review was unavailable in this session; it is not claimed as completed.

Rebuild with `python dashboard-src/subjects/polity/rebuild_all_polity.py`. The original source PDF is checked against its recorded SHA-256 and remains unchanged. The active folder is `Indian_Polity_and_Governance`; legacy `Indian_Polity_2026` is outside this rebuild.

Machine evidence: [coverage_ledger.json](coverage_ledger.json), including every page, chapter and source item. Counts in the validator are derived from source evidence rather than frozen to the previous erroneous 1,280-item bank.

## Chapter ledger

| Chapter | PDF file pages | All-exam cards | Scored UPPSC | UPPSC review |
|---|---:|---:|---:|---:|
| 1. The Constitutional Development of India | 7-17 | 44 | 21 | 0 |
| 2. Constituent Assembly and Making of the Constitution | 17-29 | 73 | 33 | 1 |
| 3. Important Committees of Constituent Assembly | 29-31 | 13 | 8 | 0 |
| 4. Sources of the Constitution | 31-37 | 29 | 19 | 0 |
| 5. Parts of Indian Constitution | 37-41 | 20 | 17 | 0 |
| 6. Articles of the Constitution | 41-50 | 29 | 17 | 2 |
| 7. Schedules | 50-61 | 64 | 32 | 0 |
| 8. The Preamble | 61-69 | 51 | 25 | 2 |
| 9. The Governance System | 69-87 | 83 | 39 | 1 |
| 10. National Symbols | 87-90 | 16 | 5 | 0 |
| 11. States and Union Territories | 90-102 | 67 | 32 | 3 |
| 12. The Citizenship | 102-105 | 17 | 9 | 0 |
| 13. Fundamental Rights | 105-136 | 169 | 91 | 1 |
| 14. Directive Principles of State Policy | 136-150 | 68 | 38 | 0 |
| 15. Fundamental Duties | 150-156 | 41 | 21 | 0 |
| 16. The President | 156-179 | 135 | 64 | 3 |
| 17. The Vice-President | 179-184 | 23 | 10 | 1 |
| 18. The Council of Ministers | 184-199 | 92 | 31 | 0 |
| 19. The Attorney General and the C.A.G. | 199-210 | 63 | 33 | 1 |
| 20. Order of Precedence | 210-212 | 7 | 0 | 0 |
| 21. The Parliament (1) | 212-231 | 108 | 38 | 6 |
| 22. The Parliament (2) | 231-243 | 64 | 28 | 3 |
| 23. The Parliament (3) | 243-269 | 142 | 75 | 1 |
| 24. Parliamentary Committees | 269-277 | 38 | 20 | 1 |
| 25. The Parliamentary Act | 277-295 | 93 | 24 | 1 |
| 26. The Supreme Court | 295-320 | 127 | 55 | 3 |
| 27. The Governor | 320-331 | 56 | 27 | 0 |
| 28. The State Legislature | 331-347 | 86 | 33 | 2 |
| 29. The High Court | 347-356 | 43 | 12 | 2 |
| 30. The Centre-State Relations | 356-367 | 58 | 33 | 1 |
| 31. Emergency Provisions | 367-375 | 39 | 19 | 2 |
| 32. The Finance Commission | 375-381 | 30 | 18 | 0 |
| 33. The Planning Commission/NITI Aayog | 381-386 | 35 | 21 | 0 |
| 34. Lokpal and Important Commissions | 386-408 | 123 | 36 | 2 |
| 35. Temporary, Transitional and Special Provisions | 408-410 | 14 | 6 | 3 |
| 36. Election Commission | 410-424 | 63 | 29 | 1 |
| 37. Political Parties | 424-436 | 57 | 18 | 2 |
| 38. Constitutional Amendments | 436-454 | 90 | 38 | 0 |
| 39. Official Language | 454-459 | 26 | 11 | 3 |
| 40. Panchayati Raj and Community Development | 459-498 | 222 | 83 | 3 |
| 41. Special Provision for Certain Classes | 498-504 | 29 | 6 | 2 |
| 42. Miscellaneous | 504-530 | 141 | 38 | 4 |
