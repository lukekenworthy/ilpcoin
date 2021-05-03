# MacOS Only! Runs the queue, a miner, and two verifiers. Then invokes a sample customer script, which posts some Ilps to the queue.
osascript -e 'tell app "Terminal" to do script "ilp-queue"';
osascript -e 'tell app "Terminal" to do script "sleep 2; sample_customer"';
osascript -e 'tell app "Terminal" to do script "sleep 4; verifier -id 1"';
osascript -e 'tell app "Terminal" to do script "sleep 4; verifier -id 2"';
osascript -e 'tell app "Terminal" to do script "sleep 6; miner -id 101 &"'
