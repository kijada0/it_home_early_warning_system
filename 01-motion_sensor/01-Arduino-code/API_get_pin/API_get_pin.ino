#include "Arduino.h"
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
 
const char* ssid = "KrólestwoNauki";
const char* password = "53357007";
 
ESP8266WebServer server(80);

IPAddress local_IP(192, 168, 0, 121);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

void basicResponse(){
  server.send(200, "text/html", "Welcome to the EWS - Early Warning System \nAPI GET: \"/event\" to read events");
}

void getEvent(){
  String message = String(digitalRead(4));
  server.send(200, "text/html", message);
}
 
// Define routing
void restServerRouting() {
    server.on("/", HTTP_GET, basicResponse);
    server.on("/event", HTTP_GET, getEvent);
}
 
// Manage not found URL
void handleNotFound() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";
  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }
  server.send(404, "text/plain", message);
}
 
void setup(void) {
  Serial.begin(115200);
  Serial.println("");

  WiFi.mode(WIFI_STA);
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  }

  WiFi.begin(ssid, password);
  Serial.println("");
  
  Serial.println("");
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  restServerRouting();
  server.onNotFound(handleNotFound);
  server.begin();
  Serial.println("HTTP server started");
}
 
void loop(void) {
  server.handleClient();
}
