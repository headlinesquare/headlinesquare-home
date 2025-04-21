# README

Version: 04/19/2025 

Author: Thomas

## Introduction

**This is the home of HeadlineSquare** ([https://headlinesquare.github.io/](https://headlinesquare.github.io/ "https://headlinesquare.github.io/")), **an experimental blog site that publishes daily U.S. news briefing in academic style.** It strives to be factual, neutral, and concise. It aims at providing a factual common ground for people who seek truth in turbulent times. It tries to maps out messy and contradictory news reports and teaches us the most important stories of the day in the shortest time. **And, it is 100% run by an AI Agent, Dr. Headline, entirely free, open-source, and transparent.** I believe this is probably one of the first systems of its kind, which may be game-changing to AI + news applications. This may set up an example that how advanced AI can guide us out of confusion rather than amplifying existing confusion.

## Motivation

Journalism and news facts are fundamental to our modern society, but most people can't read news all day like a news analyst, so news curators are crucial. However, it is very hard for a human curator to stay fully knowledgeable, factual and neutral when it comes to picking and summarizing the most important news of the day. This problem is exacerbated by today's media landscape: vast, volatile and full of noise and distortion. Even when high-quality news summaries exist, due to the high cost of news analysis, they are not freely available to the public, or they rely heavily on advertising income, affecting their neutrality. 

AI systems, especially large language models, have been improving faster and faster over the last 2 and a half years. This gives us an unprecedented opportunity. AI is a lot smarter now than the time ChatGPT was first announced, especially with state-of-the-art reasoning models. AI makes errors, but so do humans. Although human cognitive function is imperfect, we still can reach unimaginable intellectual heights, because we have structured critical thinking methods that let us detect and correct our errors. I believe this applies to AI systems as well. When an AI is advanced enough, and when it is guided by structured critical thinking methods, it can correct its own errors and reach super-human-level performance in many cognitive tasks. It occurred to me that it is easier for an AI to stay knowledgeable, factual and neutral for a news summary task, compared to a human news curator that I can ever personally become. 

That is why I created Dr. Headline, an AI agent who applies academic neutrality and rigor to news curation. The initial idea of Dr. Headline came to me on March 16, 2025. But I am not a professional software developer. I am just a young hobbyist, working part-time on this. I knew absolutely nothing about web scraping, OpenAI API, LLM orchestration, and blog hosting. It won't ever be possible if I didn't collaborate with AI for this project. 

## Main Workflow

This repository is the home of HeadlineSquare and Dr. Headline. At this time, Dr. Headline already has agentic behavior, but it is still a fixed workflow made of scripts and LLM orchestration. It fulfills its narrowly defined job with patience, precision, flexibility and transparency, which are significantly beyond the performance of state-of-the-art general-purpose agentic AIs, like ChatGPT Deep Research (announced on February 2, 2025), and ChatGPT o3, o4-mini-high (both announced on April 16, 2025). Unfortunately, it is not yet possible to process all data in one LLM prompt and generate good answers, even if the LLM is agentic. So, we must use multi-step, detailed prompts to guide the LLMs, asking them to critically evaluate their previous work and correct their errors, to generate high-quality results. Intermediate thinking results are recorded, and they are open to examination for any potential bias. 

The LLMs used by Dr. Headline are right now OpenAI o3-mini-high (announced January 31, 2025), and Anthropic Claude 3.7 Sonnet Thinking (announced February 24, 2025) , and we are continuously looking into newer LLMs. 

In this early experimental phase, Dr. Headline refers to two major Reddit news communities, r/politics, and r/Conservative, to write two daily briefings per day. It picks up ~50 best news headlines within ~350 candidates from r/politics, and another ~50 best news headlines within ~100 candidates from r/Conservative. And then it orchestrates 25 steps of LLM reasoning steps in a multi-turn conversation form, guiding the LLM with detailed prompts in each step. It writes the final document entirely by itself, weaving the headlines into narratives, and automatically uploads the documents to the blog site HeadlineSquare. Each daily briefing is 1500-2000 words long, containing layered key stories, and with accurate citations for each claim. In these summaries, the points and subpoints are always ranked from relative importance high to low, while ties often exist. HeadlineSquare has been working smoothly since April 6th, 2025, posting news by 9 pm ET, summarizing a 24-hour coverage window ending at 7 pm ET. Interestingly, Dr. Headline is both a news analyst and a historian. The daily news briefings are also a form of historic archive. Dr. Headline is also doing the work back into history, although that takes more manual tweaking. At the moment, it goes back to March 31, 2025.

## File Structure

```plaintext
headlinesquare-home/
├── automatic_summary/
├── documentation/
├── my-hugo-blog/
├── reddit_scrapper/
├── daily_job.bat
└── newsroom_daily_work.py
└── README.md
```

At this moment, the source code of HeadlineSquare has only been tested on Windows 11. Building cross-platform compatibility is underway.

In the depository, `my-hugo-blog` contains the entire Hugo static blog generator and the generated static site `headlinesquare.github.io`. `documentation` contains the top-level documents in Markdown format. And `daily_job.bat`, `newsroom_daily_work.py`, and `reddit_scrapper/`, `automatic_summary/` are all parts of Dr. Headline AI Agent workflow.

`daily_job.bat` is an startup script which relies on Windows Task Scheduler to wake up Dr. Headline daily. 

`newsroom_daily_work.py` is the highest-level orchestrator, which controls all three modules: `reddit_scraper/`, which collects news from Reddit, `automatic_summary/`, which runs the LLM orchestration to produce the daily news briefing, and `my-hugo-blog/`, which generates and updates the blog site. `reddit_scraper/` and `automatic_summary/`, `my-hugo-blog/` all contain their own subfolders and documentations.

## Folder-as-module, File-as-pipeline Architecture

One thing special about this package is that all scripts rely on relative paths and live in their own folders. They do not import other scripts in their own folders or their subfolders. There is no global namespace or memory-based state passing between scripts. All input and output flows are achieved by plain-text disk file operations, rather than passing parameters and states in the memory. In this way, all input and output parameters become fully recorded and ready for inspection at any time. 

Every module lives in a folder, with one or a few scripts directly in it, and also I/O fires or subfolders, and a documentation subfolder, and possibly a processing subfolder, which contain the folders for submodule instances, and possibly a process template subfolder, which contains the submodule instance templates. Each module minds its own business, never reaching out of their folders, and they also never touch the operations in their submodule folders, except providing input and output files.

Each module may have several submodules. To call them, the module prepares input files for the submodules, runs the submodules as subprocesses and sometimes by creating a new submodule instance for each call due to the complexity, and collects output files from the submodules, and continues the main process, and finally generates output file. For example, `automatic_summary/` is the LLM orchestration module, and it has two submodules. Because the task of submodules is complex, to avoid clogging up the file namespace, each time `automatic_summary` is given a new task, it creates new instances of submodules as new subfolders based on templates, including the copies of the submodule scripts. 

In this way, every intermediate result is written down in a file and a folder, and to debug a specific module, we simply inspect its records for input, output and intermediate results. Even when the submodule scripts are updated later, the older submodule instance folders still contain their "fossilized" version of the scripts, and they can run independently of the parent module.

To test a specific module, we simply revert it to the state that it has given inputs but not run yet, and then execute the scripts in a pre-defined way. This is easy because all the inputs are already provided in file form, and the module does not have any external dependencies other than the inputs, so the command lines to execute the scripts are very simple.

This folder-as-module, file-as-pipeline design makes building, debugging, testing, inspecting the project very easy. It may feel primitive, but it is good enough to make this project work with minimal effort.

## Installation

Running this package requires several steps or preparation. All scripts are written in`Python 3.7+`.  The newest version of Python is recommended.

Apart from standard Python libraries, external dependencies include:

`reddit_scrapper` module needs `requests`, `pytz`, and `beautifulsoup4`.

`automatic_summary` module needs `openai`, `streamlit`.

`my-hugo-blog` module needs `hugo`.

On my Windows computer, my Python environment is Anaconda 3, and I run everything with Anaconda Prompt.

```powershell
conda install requests pytz beautifulsoup4 openai streamlit
```

Otherwise, we can do

```powershell
pip install requests pytz beautifulsoup4 openai streamlit
```

However, `hugo` is always provided as a binary installation, so it needs to be manually downloaded, unzipped, and for Windows, its installation folder should be added to Environment Variables `%Path%`. For Linux, the installation is different.

For example, for Debian and Ubuntu (and derivatives),

```bash
sudo apt update
sudo apt install hugo
```

And importantly, our `automatic_summary` module requires an environment variable `%OPENROUTER_API_KEY%` which is the API Key of OpenRouter, our unified LLM API provider. Running cutting-edge LLMs for a complex task like Dr. Headline is still a bit expensive. At the moment, the price tag of running Dr. Headline every day is around $10 per day. We do not have a central API account. To bear this cost in a decentralized way, our current recommendation is that for any user who wants to run Dr. Headline, they need to buy their own LLM tokens from OpenRouter by setting up their own OpenRouter API Key. 

## Conclusion

This project is still in its infancy. Please be aware that errors can happen. Everything you see and read is experimental. Evaluate the content carefully. Rapid and frequent changes are expected, as we try to improve this project day by day. 

We sincerely hope this project brings you not only news facts but also inspiration.

## Licensing Statement

This AI news application (Dr. Headline) will be open-source and licensed under the GNU General Public License v3.0 (GPLv3). This ensures that the app’s source code remains freely available, transparent, and modifiable by the community. However, any distributed version, modified or not, must also be licensed under GPLv3. See the full license at https://www.gnu.org/licenses/gpl-3.0.html.

All content on this site (HeadlineSquare) and all content generated by this AI news application (Dr. Headline) are released under the Creative Commons Zero (CC0 1.0) License. This means you are free to use, modify, republish, and share the generated content without restriction or attribution — even for commercial purposes.
