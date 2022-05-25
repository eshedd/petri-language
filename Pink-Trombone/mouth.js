const ws = new WebSocket("ws://localhost:5678/");
var ctx;
var analyser;
var DEFAULT_LISTEN_INTERVAL = 10;
var DEFAULT_RECORD_DURATION = 1000;
function prepareMouth(){
    ctx = pinkTromboneElement.pinkTrombone.audioContext;
    analyser = ctx.createAnalyser();
    analyser.fftSize = 2048;
    pinkTromboneElement.pinkTrombone.connect(analyser);
    analyser.connect(ctx.destination);
};
var dataFull = [];
function recordData() {
    var data = new Float32Array(analyser.frequencyBinCount);
    analyser.getFloatFrequencyData(data);
    dataFull.push(data);
}
var recordInterval;
function startListening(interval = DEFAULT_LISTEN_INTERVAL) {
    recordInterval = setInterval(recordData, interval);
}
var encodedURI;
function sendData() {
    clearInterval(recordInterval);
    console.log(dataFull);
    dataFull = [];
}
function recordForDuration(listenInterval = DEFAULT_LISTEN_INTERVAL, recordDuration = DEFAULT_RECORD_DURATION) {
    startListening(listenInterval);
    setTimeout(saveData, recordDuration);
}
ws.onmessage = function (event) {
    params = event.data.split('|').map(Number);
    startListening();
    say({ index: params[0], diameter: params[1] }, { index: params[2], diameter: params[3] }, params[4], params[5], params[6], params[7], params[8]).then(() => { sendData(); shutUp(); });
};

