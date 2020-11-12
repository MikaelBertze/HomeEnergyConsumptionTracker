#include "wifi-credentials.h"
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include "music.h"
#include <Ticker.h>
#include <ArduinoOTA.h>

Ticker toneTicker;
WiFiServer server(80);

const int SONG_starwars = 1;
const int SONG_harryPotter = 2;
const int SONG_babyElephant = 3;
const int SONG_happyBirthday = 4;

const int loops = 5;


int *currentSong;
volatile int songIdx;
volatile int songLength;
volatile int skip;
volatile int loopCount = 0;


void play(int song){
  loopCount = 0;
  pinMode (D1, OUTPUT );
  switch(song) {
    case 0:
      currentSong = 0;
      break;
    case SONG_starwars:
      songLength = sizeof(starwars)/sizeof(starwars[0]);
      currentSong = starwars;
      break;
    case SONG_harryPotter:
      songLength = sizeof(harry_potter)/sizeof(harry_potter[0]);
      currentSong = harry_potter;
      break;
    case SONG_babyElephant:
      songLength = sizeof(baby_elephant)/sizeof(baby_elephant[0]);
      currentSong = baby_elephant;
      break;
    case SONG_happyBirthday:
      songLength = sizeof(happy_birthday)/sizeof(happy_birthday[0]);
      currentSong = happy_birthday;
      break;
  }
  songIdx = 0;
  //currentSong = song;
  Serial.print("Song length:");
  Serial.println(songLength);
}

void tone_changer() {
  if (currentSong == 0){
    digitalWrite(D1,1);
    return;
  }
  if (--skip > 0) {
    //Serial.print("skip: ");
    //Serial.println(skip);
    return;
  }
  if (songIdx >= songLength) {
    loopCount++;
    if (loopCount > loops)
      currentSong = 0;
    else
      songIdx = 0;
    
    digitalWrite(D1,1);
    Serial.println("Song done!");
    return;
  }

  Serial.print("New tone! ");
  Serial.println(currentSong[songIdx]);
  // start tone
  if (currentSong[songIdx] == REST) {
    digitalWrite(D1,1);
  }
  else {
    analogWriteFreq(currentSong[songIdx]);
    analogWrite(D1,500);
  }
  skip = 8/currentSong[songIdx + 1];
  songIdx+=2;
}

void tone_x(uint8_t _pin, unsigned int frequency, unsigned long duration) {
  pinMode (_pin, OUTPUT );
  analogWriteFreq(frequency);
  analogWrite(_pin,500);
  delay(duration);
  digitalWrite(_pin,1);

}

void setup() {
  toneTicker.attach(1.5/8, tone_changer);
  WiFi.mode(WIFI_STA);
  WiFi.setPhyMode(WIFI_PHY_MODE_11G);
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  delay(10);
 
  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(SSID);
  Serial.println(password);
 
  WiFi.begin(SSID, password);
 
  while (WiFi.status() != WL_CONNECTED) {
     delay(500);
     Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
 
  // // Start the server
  server.begin();
  Serial.println("Server started");
 
  // // Print the IP address
  Serial.print("Use this URL : ");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");

  if (!MDNS.begin("alarmthingy")) {             // Start the mDNS responder for esp8266.local
    Serial.println("Error setting up MDNS responder!");
  }
  Serial.println("mDNS responder started");
 

  tone_x(D1, 880, 100);

  ArduinoOTA.onStart([]() {
    Serial.println("Start");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });
  ArduinoOTA.begin();

}
 
void loop() {
  MDNS.update();
  ArduinoOTA.handle();
  
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }
 
  // Wait until the client sends some data
  Serial.println("new client");
  while(!client.available()){
    delay(1);
  }
 
  // Read the first line of the request
  String request = client.readStringUntil('\r');
  Serial.println(request);
  client.flush();
 
  // Match the request
 
  if (request.indexOf("/starwars") != -1) {
    //digitalWrite(ledPin, HIGH);
    play(SONG_starwars);
  } 
  if (request.indexOf("/harrypotter") != -1) {
    //digitalWrite(ledPin, HIGH);
    play(SONG_harryPotter);
  }
  if (request.indexOf("/babyelephant") != -1) {
    //digitalWrite(ledPin, HIGH);
    play(SONG_babyElephant);
  }
  if (request.indexOf("/happybirthday") != -1) {
    //digitalWrite(ledPin, HIGH);
    play(SONG_happyBirthday);
  } 
  if (request.indexOf("/stop") != -1) {
    //digitalWrite(ledPin, HIGH);
    play(0);
  } 
  
   
  // if (request.indexOf("/mission_impossible") != -1){
  //   //digitalWrite(ledPin, LOW);
  //   play(1);
  // }
 
  // Return the response
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println(""); //  do not forget this one
  client.println("<!DOCTYPE HTML>");
  client.println("<html>");
 
  client.print("<h1>Songs</h1>");
 
  client.println("<br><br>");
  client.println("<a href=\"/starwars\">Starwars</a><br>");
  client.println("<a href=\"/harrypotter\">Harry potter</a><br>");
  client.println("<a href=\"/babyelephant\">Baby elephant</a><br>");
  client.println("<a href=\"/happybirthday\">Happy Birthday</a><br>");
  client.println("<br>");
  client.println("<a href=\"/stop\">STOP!</a><br>");
  
  client.println("</html>");
 
  delay(1);
  Serial.println("Client disconnected");
  Serial.println("");
 
}
