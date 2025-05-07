+++
date = '2025-05-06T20:00:00-05:00'
draft = false
author = 'Thomas'
title = '[Patch Notice] HeadlineSquare HTML rendering bug, all clear now.'
+++

Semicolons were often added to the end of URLs, especially in r/Conservative summaries, and they became a part of the hyperlinks wrongly, making some of the hyperlinks unusable.

I often randomly test the hyperlinks and they all worked, but I just realized that I only test the longest hyperlinks, because I thought they were the ones more prone to hallucinations. I didn't find any hallucinations.

But yesterday I clicked some of the simpler links of r/Conservative summaries and I got 30% of them not working. I panicked because I thought the hallucination caught me off guard, but then I realized all the links were real, but they each got an additional ";" attached to them, which was redundant.

The links themselves were correct but the semicolons I used to declare the end of line was wrongly identified as part of the URLs. The fix was simple. I removed all redundant semicolons from all my current and previous output documents.

I am really surprised of this bug because it affected so many links but it evaded my "random" sampling for so long, because I didn't test the rendered URL links very thoroughly, and I thought very long and complex links were at higher risks of hallucination, so I tested those a lot. Weird enough, those never had problems, but the shorter, simpler links did. I am very sorry for the potential confusion it might have created.
