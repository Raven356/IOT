#include <Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <LSM303.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

#include <C:\\secret\\wifipass.txt> // ssid and pass
//const char *ssid = "ssid";
//const char *pass = "pass"; 

const char *mqtt_server = "192.168.0.20";
const int mqtt_port = 1883;

const bool print_debug = false;

// fake gps start point
double longitude = 50.466329; 
double latitude = 30.512865;

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "ntp1.time.in.ua");

WiFiClient wclient;
PubSubClient client(wclient);

LSM303 compass;

char buf[80];
char time_buf[200];
char json[2048];

void setup()
{
  Serial.begin(9600);
  Wire.begin(D1, D2);
  compass.init();
  compass.enableDefault();
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);

  compass.m_min = (LSM303::vector<int16_t>){-328,   -850,   -421};
  compass.m_max = (LSM303::vector<int16_t>){+835,   +278,   +721};
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  timeClient.begin();
  timeClient.update();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client";
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop()
{
  if (WiFi.status() != WL_CONNECTED) 
    setup_wifi();
  else{
    if (!client.connected()) 
      reconnect();
    
    client.loop();

    compass.read();
    double a = compass.heading() - 90;
    if(print_debug){
      snprintf(buf, sizeof(buf), "%6d, %6d, %6d, %6d, %6d, %6d, %f",
        compass.a.x, compass.a.y, compass.a.z,
        compass.m.x, compass.m.y, compass.m.z, a);

      Serial.println(buf);
    }

    const double speed = 0.00005;
    longitude += cos(a*M_PI/180.0)*speed, latitude += sin(a*M_PI/180.0)*speed;

    {
      time_t epochTime = timeClient.getEpochTime();
      struct tm *ptm = gmtime ((time_t *)&epochTime); 

      snprintf(time_buf, sizeof(time_buf), 
        "%04d-%02d-%02dT%02d:%02d:%02d.000000",
        ptm->tm_year+1900, ptm->tm_mon+1, ptm->tm_mday, ptm->tm_hour, ptm->tm_min, ptm->tm_sec
      );
      //Serial.println(time_buf);
    }

    snprintf(json, sizeof(json), 
      "{\"accelerometer\":{\"x\":%d,\"y\":%d,\"z\":%d},"\
      "\"gps\":{\"longitude\":%.10f, \"latitude\":%.10f},"\
      "\"timestamp\": \"%s\","\
      "\"user_id\":\"esp8266\"}",
      compass.a.x, compass.a.y, compass.a.z,
      longitude, latitude, time_buf);
    
    client.publish("agent_data_topic", json);

    delay(10);
  }
}