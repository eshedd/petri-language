const ws = new WebSocket("ws://localhost:5678/");
var ctx;
var analyser;
var DEFAULT_LISTEN_INTERVAL = 10;
var DEFAULT_RECORD_DURATION = 1000;
function prepareMouth(){
    ctx = pinkTromboneElement.pinkTrombone.audioContext;
    analyser = ctx.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0;
    pinkTromboneElement.pinkTrombone.connect(analyser);
    analyser.connect(ctx.destination);
    window.addEventListener("keypress", event => {

        baseFrequency = pinkTromboneElement.parameters.frequency.value;
        //window.sayUKATON();
        // say(12.9, 0.9, 1.5, 1, 0.7, 0.6, 440).then(() => {
        //     say(12.9, 0.9, 0.5, 1, 0.7, 0.6, 880).then(() => {
        //         say(12.9, 0.9, 1.5, 1, 0.7, 0.6, 120).then(shutUp)
        //     })
        // })

        // say(12.9, 0.9, 1.5, 1, 0.7, 0.6, 120)
        // say(12.9, 0.9, 1.5, 1, 0.7, 0.6, 200)
        // shutUp()
        say({ index: randomNumber(6, 35), diameter: randomNumber(1, 5) }, { index: randomNumber(-50, 50), diameter: randomNumber(-1, 35) }, randomNumber(0, 5), randomNumber(0.2, 3), randomNumber(0, 1), randomNumber(0, 1), randomNumber(20, 1000)).then(shutUp)
    })
};
var dataFull = [];
function recordData() {
    var data = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(data);
    dataFull.push(data);
}
var recordInterval;
function startListening(interval = DEFAULT_LISTEN_INTERVAL) {
    recordInterval = setInterval(recordData, interval);
}
function sendData() {
    clearInterval(recordInterval);
    for(i in dataFull){
        ws.send(`S:${i}/${dataFull.length-1}`);
        ws.send(dataFull[i].buffer);
    }
    // console.log(dataFull)
    dataFull = [];
}
function recordForDuration(listenInterval = DEFAULT_LISTEN_INTERVAL, recordDuration = DEFAULT_RECORD_DURATION) {
    startListening(listenInterval);
    setTimeout(saveData, recordDuration);
}
ws.onmessage = function (event) {
    // console.log(event);
    if(event.data[0] == "M"){   
        params = event.data.split('|').map(Number);
        startListening();
        say({ index: params[0], diameter: params[1] }, { index: params[2], diameter: params[3] }, params[4], params[5], params[6], params[7], params[8]).then(() => { sendData(); shutUp(); });
    }
};

