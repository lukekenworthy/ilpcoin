# ilp-queue&>/dev/null  &
# sleep 2; sample_customer &
# sleep 4; verifier -id 1&>/dev/null  &
# sleep 6; miner -id 101&>/dev/null  &


osascript -e 'tell app "Terminal" to do script "ilp-queue"';
osascript -e 'tell app "Terminal" to do script "sleep 2; sample_customer"';
osascript -e 'tell app "Terminal" to do script "sleep 4; verifier -id 1"';
osascript -e 'tell app "Terminal" to do script "sleep 4; verifier -id 2"';
osascript -e 'tell app "Terminal" to do script "sleep 6; miner -id 101 &"'
