#property strict

input string BridgeURL = "http://127.0.0.1:8000/ingest/mt5";
input string SourceAccountName = "master-demo-1";

string EscapeJson(string value)
{
   StringReplace(value, "\\", "\\\\");
   StringReplace(value, "\"", "\\\"");
   StringReplace(value, "\n", "\\n");
   StringReplace(value, "\r", "\\r");
   StringReplace(value, "\t", "\\t");
   return value;
}

string BuildTimestamp()
{
   datetime now = TimeCurrent();
   return TimeToString(now, TIME_DATE|TIME_SECONDS);
}

bool SendJsonToBridge(string json)
{
   char post[];
   char result[];
   string headers = "Content-Type: application/json\r\n";
   string response_headers;
   int timeout = 5000;

   StringToCharArray(json, post, 0, WHOLE_ARRAY, CP_UTF8);

   ResetLastError();
   int res = WebRequest(
      "POST",
      BridgeURL,
      headers,
      timeout,
      post,
      result,
      response_headers
   );

   if(res == -1)
   {
      Print("WebRequest failed. Error: ", GetLastError());
      return false;
   }

   string response = CharArrayToString(result);
   Print("Bridge response: ", response);
   return true;
}

string BuildOpenEventJson(string sourceTicket, string symbol, string side, double volume, double price, double stopPrice, double tp, long magic, string comment)
{
   string eventId = "mt5-" + sourceTicket + "-OPEN-" + IntegerToString((int)TimeCurrent());

   string json =
      "{"
      "\"event_id\":\"" + EscapeJson(eventId) + "\","
      "\"source_platform\":\"mt5\","
      "\"source_account\":\"" + EscapeJson(SourceAccountName) + "\","
      "\"source_ticket\":\"" + EscapeJson(sourceTicket) + "\","
      "\"action\":\"OPEN\","
      "\"symbol\":\"" + EscapeJson(symbol) + "\","
      "\"side\":\"" + EscapeJson(side) + "\","
      "\"volume\":" + DoubleToString(volume, 2) + ","
      "\"price\":" + DoubleToString(price, _Digits) + ","
      "\"stopPrice\":" + DoubleToString(stopPrice, _Digits) + ","
      "\"tp\":" + DoubleToString(tp, _Digits) + ","
      "\"magic\":" + IntegerToString((int)magic) + ","
      "\"comment\":\"" + EscapeJson(comment) + "\","
      "\"timestamp\":\"" + EscapeJson(BuildTimestamp()) + "\""
      "}";

   return json;
}

string BuildCloseEventJson(string sourceTicket, string symbol)
{
   string eventId = "mt5-" + sourceTicket + "-CLOSE-" + IntegerToString((int)TimeCurrent());

   string json =
      "{"
      "\"event_id\":\"" + EscapeJson(eventId) + "\","
      "\"source_platform\":\"mt5\","
      "\"source_account\":\"" + EscapeJson(SourceAccountName) + "\","
      "\"source_ticket\":\"" + EscapeJson(sourceTicket) + "\","
      "\"action\":\"CLOSE\","
      "\"symbol\":\"" + EscapeJson(symbol) + "\","
      "\"volume\":0.0,"
      "\"timestamp\":\"" + EscapeJson(BuildTimestamp()) + "\""
      "}";

   return json;
}

string BuildModifyEventJson(string sourceTicket, string symbol, double stopPrice, double tp)
{
   string eventId = "mt5-" + sourceTicket + "-MODIFY-" + IntegerToString((int)TimeCurrent());

   string json =
      "{"
      "\"event_id\":\"" + EscapeJson(eventId) + "\","
      "\"source_platform\":\"mt5\","
      "\"source_account\":\"" + EscapeJson(SourceAccountName) + "\","
      "\"source_ticket\":\"" + EscapeJson(sourceTicket) + "\","
      "\"action\":\"MODIFY_SLTP\","
      "\"symbol\":\"" + EscapeJson(symbol) + "\","
      "\"volume\":0.0,"
      "\"stopPrice\":" + DoubleToString(stopPrice, _Digits) + ","
      "\"tp\":" + DoubleToString(tp, _Digits) + ","
      "\"timestamp\":\"" + EscapeJson(BuildTimestamp()) + "\""
      "}";

   return json;
}

int OnInit()
{
   Print("CopierEA initialized.");
   Print("IMPORTANT: Add this URL to MT5 WebRequest allowed list: ", BridgeURL);
   return(INIT_SUCCEEDED);
}

void OnTradeTransaction(
   const MqlTradeTransaction &trans,
   const MqlTradeRequest &request,
   const MqlTradeResult &result
)
{
   // Stage 1 simplified logic:
   // - detect deal add
   // - send OPEN or CLOSE
   // - detect SL/TP modifications when possible

   if(trans.type == TRADE_TRANSACTION_DEAL_ADD)
   {
      ulong dealTicket = trans.deal;
      if(!HistoryDealSelect(dealTicket))
      {
         Print("Failed to select deal: ", dealTicket);
         return;
      }

      string symbol = HistoryDealGetString(dealTicket, DEAL_SYMBOL);
      long entry = HistoryDealGetInteger(dealTicket, DEAL_ENTRY);
      long dealType = HistoryDealGetInteger(dealTicket, DEAL_TYPE);
      double volume = HistoryDealGetDouble(dealTicket, DEAL_VOLUME);
      double price = HistoryDealGetDouble(dealTicket, DEAL_PRICE);
      long magic = HistoryDealGetInteger(dealTicket, DEAL_MAGIC);
      string comment = HistoryDealGetString(dealTicket, DEAL_COMMENT);
      ulong positionId = (ulong)HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID);

      if(entry == DEAL_ENTRY_IN)
      {
         string side = (dealType == DEAL_TYPE_BUY) ? "BUY" : "SELL";
         string json = BuildOpenEventJson(
            IntegerToString((int)positionId),
            symbol,
            side,
            volume,
            price,
            0.0,
            0.0,
            magic,
            comment
         );
         SendJsonToBridge(json);
      }
      else if(entry == DEAL_ENTRY_OUT)
      {
         string json = BuildCloseEventJson(
            IntegerToString((int)positionId),
            symbol
         );
         SendJsonToBridge(json);
      }
   }

   // You can extend this later with more precise modify detection.
}