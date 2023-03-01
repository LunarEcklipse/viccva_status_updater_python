# ViccValentine's Status Updater (Python)
This Python Script was written to capture a friend's Twitch stream status using the Twitch RESTful API over the course of a few days in February 2022. It uses timers to automatically refresh its authorization key, and requested the state every 60 seconds before publishing it to a local JSON file. This was ultimately written as more of a proof-of-concept above all else; the script required a constant ~27 mb of memory to operate, something that weighed fairly heavily on my Raspberry Pi. I later decided to rewrite this script in [Rust](https://github.com/LunarEcklipse/viccva_status_updater_rust), but decided to archive the python version anyways, as my Github sort of serves as a semi-portfolio that journals my learning of programming.

## Things I learned from this:
• RESTful API utilization and network errors  
• Acquisition and maintenance of authorization keys  
• A simple blocking event loop. I had an non-blocking event loop implemented and working utilizing async/await, but I had concerns about potential issues regarding reauthorization that unexpected behavior may arise if the script attempted to update data while acquiring and writing the authorization; something that I had at the time not figured out a solution for.

## Things I would do differently:
• Utilization of a mutex variable. This solves the problem I had with the event loop as I would be able to control data access to my authorization variable during updating it.  
• Better memory optimization. I'm not an expert on optimizing python memory, but I was unhappy with the usage, which seemed to average around a consistent 27.3 megabytes of usage. I don't have any benchmarks on whether or not that usage is good, but I was still unhappy with it due to the amount of memory already in use on the server the script was hosted on. The Rust version I wrote later only required approximately a third of the memory of this (specifically 9.8 mb over 27.3, about 35.8%), so while Python suffers as an interpreted language there must be something I can do to alleviate this usage.  
