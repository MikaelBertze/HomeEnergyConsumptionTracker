#include "esp_camera.h"
#include <WiFi.h>
#include <ArduinoOTA.h>
#include <WebServer.h>
extern "C" {
#include "crypto/base64.h"
#include "dl_lib_matrix3d.h"
#include "math.h"
//#include <PubSubClient.h>
#include <mqttreporter.h>
#include "wifi-credentials.h"

}
#define LED_BUILTIN 4
//#define LED_ON
//
// WARNING!!! PSRAM IC required for UXGA resolution and high JPEG quality
//            Ensure ESP32 Wrover Module or other board with PSRAM is selected
//            Partial images will be transmitted if image exceeds buffer size
//

// Select camera model
//#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
//#define CAMERA_MODEL_ESP_EYE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_PSRAM // Has PSRAM
//#define CAMERA_MODEL_M5STACK_V2_PSRAM // M5Camera version B Has PSRAM
//#define CAMERA_MODEL_M5STACK_WIDE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_ESP32CAM // No PSRAM
#define CAMERA_MODEL_AI_THINKER // Has PSRAM
//#define CAMERA_MODEL_TTGO_T_JOURNAL // No PSRAM

#include "camera_pins.h"


/** Report struct */
typedef struct {
	int angle;
  int timespan_ms;
  bool handled;
} angle_report_t;

angle_report_t angle_report;

WebServer server(80);
bool running = false;
const char* mqtt_server = "bulbasaur.bertze.se";
const char* topic = "hallondisp_test";

//TaskHandle_t xHandle =

MqttReporter reporter({ mqtt_server, topic, "water_meter" });
//WiFiClient espClient;
//PubSubClient client(espClient);

int latestAngle = 0;

TaskHandle_t Task1;

void handleRoot();
void handleStop();
void handleStart();
void handleStatus();
void run(void * params);

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.fb_count = 1;

  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  // if(psramFound()){
  //   Serial.println("UXGA");
  //   config.frame_size = FRAMESIZE_VGA;
  //   config.jpeg_quality = 10;
  //   config.fb_count = 1;
  // } else {
  //   Serial.println("SVGA");
  //   config.frame_size = FRAMESIZE_VGA;
  //   config.jpeg_quality = 12;
  //   config.fb_count = 1;
  // }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1); // flip it back
    s->set_brightness(s, 1); // up the brightness just a bit
    s->set_saturation(s, -2); // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  //s->set_framesize(s, FRAMESIZE_QVGA);

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  //startCameraServer();


  ArduinoOTA
    .onStart([]() {
      String type;
      if (ArduinoOTA.getCommand() == U_FLASH)
        type = "sketch";
      else // U_SPIFFS
        type = "filesystem";

      // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
      Serial.println("Start updating " + type);
    })
    .onEnd([]() {
      Serial.println("\nEnd");
    })
    .onProgress([](unsigned int progress, unsigned int total) {
      Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    })
    .onError([](ota_error_t error) {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
      else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
      else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
      else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
      else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

  ArduinoOTA.begin();

  Serial.print("Camera Ready! IP:");
  Serial.print(WiFi.localIP());

  // client.setServer(mqtt_server, 1883);//connecting to mqtt server
  // client.connect("ESP32_clientID", "hallondisp", "disphallon");
  
  // client.publish("some_topic", "hello hello!");
  reporter.connect();
  reporter.report("HELLO");
#ifdef LED_ON
  pinMode (LED_BUILTIN, OUTPUT);//Specify that LED pin is output
  digitalWrite(LED_BUILTIN, HIGH);
#endif

  server.on("/", handleRoot);
  server.on("/stop", handleStop);
  server.on("/start", handleStart);
  server.on("/status", handleStatus);
  server.begin();
  Serial.println("HTTP server started");
}



int i= 0;
long t = millis();
void loop() {
  reporter.reconnectingLoop();
  //client.loop();
  // put your main code here, to run repeatedly:
  ArduinoOTA.handle();
  server.handleClient();
  if(running) {
    if (!angle_report.handled) {
      int a = angle_report.angle;
      angle_report.handled = true;
      String s = String("{ \"angle\" : \"[angle]\"}");
      s.replace("[angle]", String(a, DEC));
      reporter.report(s);
    }
  }
  // if (running)
  // {
  //   run();
  // }
}

dl_matrix3du_t * get_image(){
  camera_fb_t *fb = esp_camera_fb_get();
  dl_matrix3du_t *image_matrix = dl_matrix3du_alloc(1, fb->width, fb->height, 3);
  fmt2rgb888(fb->buf, fb->len, fb->format, image_matrix->item);
  esp_camera_fb_return(fb);
  dl_matrix3du_t *s_matrix = dl_matrix3du_alloc(1, 150, 150, 1);
  for (int i = 0; i < 150; i++) {
    for(int j = 0; j < 150; j++) {
      
      int index = (320* (i + 45) + (j + 100)) * 3;

      unsigned char r = image_matrix->item[index];
      unsigned char g = image_matrix->item[index + 1];
      unsigned char b = image_matrix->item[index + 2];
      
      double max = r;
      double min = r;
      if (g > max)
        max = g;
      if (g < min)
        min = g;
      if (b > max)
        max = b;
      if (b < min)
        min = b;
      
      max /= 255;
      min /= 255;

      double l = (min + max) / 2.0;
      double s = 0;
      if (min == max)
        s = 0;
      else if(l < .5)
        s = (max - min) / (max + min);
      else
        s = (max - min)/(2 - max - min);
      s_matrix->item[i * 150 + j] = (s > .2)? 1: 0;
    }
  }

  dl_matrix3du_free(image_matrix);
  return s_matrix;
}

int get_meter_angle(dl_matrix3du_t *s_matrix) {
  
  
  //dl_matrix3du_t *s_matrix = get_image();

  //dl_matrix3du_t *s_matrix = dl_matrix3du_alloc(1, fb->width, fb->height, 1);
  
  // Saturation
  //uc_t* buf = image_matrix->item;
  
  int forward = 0;
  int backward = 0;
  
  for (i = 0; i < 2; i++) {
    int angle = 0;
    int max_val = 0;
  
    for (int deg = (i == 0) ? 0 : 360; (i==0)? deg < 360 : deg > 0; (i == 0)? deg += 1 : deg -= 1)
    {
      
      double radians = deg*PI/180.0;

      int mid_x = 75;
      int mid_y = 80;
      int x = 60* cos(radians) + mid_x;
      int y = 60* sin(radians) + mid_y;

      int sum = s_matrix->item[y*150 + x];
      sum += s_matrix->item[y*150 + x - 1];
      sum += s_matrix->item[y*150 + x + 1];
      sum += s_matrix->item[(y - 1)*150 + x];
      sum += s_matrix->item[(y + 1)*150 + x];

      if (sum > max_val) {
        max_val = sum;
        angle = deg;
      }
      
    }
    if (i == 0)
      forward = angle;
    else
      backward = angle;
  }
  Serial.print("Forward:");
  Serial.println(forward);
  Serial.println("Backward:");
  Serial.print(backward);
  return (forward + backward) / 2;

}

void handleStart() {
  running = true;
  reporter.report("Starting reporting");
  xTaskCreatePinnedToCore(
      run, /* Function to implement the task */
      "Task1", /* Name of the task */
      10000,  /* Stack size in words */
      (void*)&angle_report,  /* Task input parameter */
      1,  /* Priority of the task */
      &Task1,  /* Task handle. */
      1); /* Core where the task should run */
  
  WiFiClient web_client = server.client();
  web_client.print("HTTP/1.1 200 OK\r\n");
}

void handleStatus() {
  WiFiClient web_client = server.client();
  web_client.print("HTTP/1.1 200 OK\r\n");
  web_client.printf("ANGLE: %d\r\n", angle_report.angle);
  web_client.printf("MS: %d\r\n", angle_report.timespan_ms);
  web_client.printf("HANDLED: %s\r\n", angle_report.handled ? "YES" : "NO");
  
}

void handleStop() {
  running = false;
  reporter.report("Stopping reporting");
  vTaskDelete(Task1);

  WiFiClient web_client = server.client();
  web_client.print("HTTP/1.1 200 OK\r\n");

}
void handleRoot() {
  Serial.println("HandleRoot");
  //int loop_time = millis();
  //int time_diff = loop_time - lastTick;
  dl_matrix3du_t *s_matrix = get_image();
  int angle = get_meter_angle(s_matrix);

  // int original_angle = angle;
  // if (angle < last_deg && angle < 170 && last_deg > 190)  // handle passing 0 deg
  //   angle += 360;
  

  // double deg_diff = angle -  last_deg;
  // double consumtion = 0;
  // double l_diff = 0;
  // if (deg_diff > 0) {
  //   lastTick = loop_time;
  //   last_deg = original_angle;
    
  //   consumtion = (double)l_diff / (time_diff / 1000);
  //   double deg_per_l = 420; 
  //   l_diff = deg_diff/deg_per_l;
  // }

  int len = s_matrix->h * s_matrix->w; // * image_matrix->c;
  
  WiFiClient web_client = server.client();
  web_client.print("HTTP/1.1 200 OK\r\n");
  web_client.print("Content-Disposition: attachment; filename=img.raw\r\n");
  web_client.print("Content-Type: application/octet-stream\r\n");
  web_client.printf("Content-Length: %d\r\n", len);
  web_client.print("Connection: close\r\n");
  web_client.print("Access-Control-Allow-Origin: *\r\n");
  web_client.printf("ANGLE: %d\r\n", angle);
  //web_client.printf("LITERS: %.4f\r\n", l_diff);
  //web_client.printf("CONSUMPTION: %.2f\r\n", consumtion);
  //web_client.printf("T_DIFF: %d\r\n", time_diff);
  web_client.print("\r\n");
  //client.write((const char*)image_matrix->item, len);
  web_client.write((const char*)s_matrix->item, len);
  //server.send(200, "text/plain", "hello");
  dl_matrix3du_free(s_matrix);

  //client.publish("some_topic", "hello hello!");
  reporter.report("hej");
}

void run( void * params ) {
  double last_deg = 0;
  long lastTick = millis();
  angle_report_t* a = (angle_report_t *) params;
  int i = 0;
  for(;;) {
    
    //delay(1000);
    //continue;
    //*a = i++;
    //latestAngle =  latestAngle++; // original_angle;
    //delay(1);
    //continue;

    // int loop_time = millis();
    // int time_diff = loop_time - lastTick;
    dl_matrix3du_t *s_matrix = get_image();
    int angle = get_meter_angle(s_matrix);
    dl_matrix3du_free(s_matrix);

    a->angle=angle;
    a->timespan_ms=millis();
    a->handled = false;

    // int original_angle = angle;
    // if (angle < last_deg && angle < 170 && last_deg > 190)  // handle passing 0 deg
    //   angle += 360;
    
    // //latestAngle = original_angle;
    // continue;


    // double deg_diff = angle -  last_deg;
    // double consumtion = 0;
    // double l_diff = 0;
    // if (deg_diff > 0) {
    //   lastTick = loop_time;
    //   last_deg = original_angle;
      
    //   consumtion = (double)l_diff / (time_diff / 1000);
    //   double deg_per_l = 420; 
    //   l_diff = deg_diff/deg_per_l;
    //   String a = "{ \"water_angle\" : " + original_angle;
    //   a += "}";
      
      //reporter.report(a);
      //delay(100);
    // }
  }

}