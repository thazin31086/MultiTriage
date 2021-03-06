using System;
using System.ServiceModel;
using System.Collections.Generic;

// These namespaces are found in the Microsoft.Xrm.Sdk.dll assembly
// located in the SDK\bin folder of the SDK download.
using BugTriageModel.Models;
using System.Configuration;
using System.Net;
using PowerApps.Samples;
using Newtonsoft.Json.Linq;
using System.Threading.Tasks;

namespace BugTriageModel.Services
{
    public static class TicketService
    {
        //Get configuration data from App.config connectionStrings
        static readonly string connectionString = ConfigurationManager.ConnectionStrings["Connect"].ConnectionString;
        static readonly ServiceConfig config = new ServiceConfig(connectionString);

  
        
        public static async Task<List<Ticket>> GetTickets()
        {
            List<Ticket> tickets = new List<Ticket>();
            try
            {
                /*Retrieve all tickets*/
                string fetchTicketQuery = "<fetch distinct='false' mapping='logical' output-format='xml-platform' version='1.0'>" +
                                             "<entity name='cr902_ticket'>" +
                                             "<attribute name='cr902_ticketid'/>" +
                                             "<attribute name='cr902_name'/>" +
                                             "<attribute name='new_type'/>" +
                                             "<attribute name='new_status'/>" +
                                             "<attribute name='new_description'/>" +
                                             //"<attribute name='new_assgintoid'/>" +
                                             "<order descending='false' attribute='cr902_name'/>" +
                                             "</entity>" +
                                             "</fetch>";

                var formattedValueHeaders = new Dictionary<string, List<string>> {
                { "Prefer", new List<string>
                    { "odata.include-annotations=\"OData.Community.Display.V1.FormattedValue\"" }
                }
            };

                using (CDSWebApiService svc = new CDSWebApiService(config))
                {
                    JToken resulttickets = svc.Get($"cr902_tickets?fetchXml={WebUtility.UrlEncode(fetchTicketQuery)}", formattedValueHeaders);
                    if (resulttickets != null)
                    {
                        foreach (var ticket in resulttickets["value"].Children())
                        {
                            Ticket newticket = new Ticket();
                            newticket.Title = ticket["cr902_name"]?.ToString();
                            newticket.Description = ticket["new_description"]?.ToString();
                           // newticket.AssignedTo = ticket["new_assginto"].ToString();
                            newticket.Status = ticket["new_status"]?.ToString();
                            newticket.Type = ticket["new_type"]?.ToString();
                            tickets.Add(newticket);
                            Console.WriteLine($"Name - {ticket["cr902_name"]}, Status - {ticket["new_status@OData.Community.Display.V1.FormattedValue"]}");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());
                throw;
            }

            return tickets;
        }

        public static void CRMConnect()
        {
            try
            {
                try
                { 
                    
                    ConnectService app = new ConnectService();
                    app.Run();
                }
                catch (FaultException<Microsoft.Xrm.Sdk.OrganizationServiceFault> ex)
                {
                    Console.WriteLine("The application terminated with an error.");
                    Console.WriteLine("Timestamp: {0}", ex.Detail.Timestamp);
                    Console.WriteLine("Code: {0}", ex.Detail.ErrorCode);
                    Console.WriteLine("Message: {0}", ex.Detail.Message);
                    Console.WriteLine("Trace: {0}", ex.Detail.TraceText);
                    Console.WriteLine("Inner Fault: {0}",
                        null == ex.Detail.InnerFault ? "No Inner Fault" : "Has Inner Fault");
                }
                catch (System.TimeoutException ex)
                {
                    Console.WriteLine("The application terminated with an error.");
                    Console.WriteLine("Message: {0}", ex.Message);
                    Console.WriteLine("Stack Trace: {0}", ex.StackTrace);
                    Console.WriteLine("Inner Fault: {0}",
                        null == ex.InnerException.Message ? "No Inner Fault" : ex.InnerException.Message);
                }
                catch (System.Exception ex)
                {
                    Console.WriteLine("The application terminated with an error.");
                    Console.WriteLine(ex.Message);

                    // Display the details of the inner exception.
                    if (ex.InnerException != null)
                    {
                        Console.WriteLine(ex.InnerException.Message);

                        FaultException<Microsoft.Xrm.Sdk.OrganizationServiceFault> fe = ex.InnerException
                            as FaultException<Microsoft.Xrm.Sdk.OrganizationServiceFault>;
                        if (fe != null)
                        {
                            Console.WriteLine("Timestamp: {0}", fe.Detail.Timestamp);
                            Console.WriteLine("Code: {0}", fe.Detail.ErrorCode);
                            Console.WriteLine("Message: {0}", fe.Detail.Message);
                            Console.WriteLine("Trace: {0}", fe.Detail.TraceText);
                            Console.WriteLine("Inner Fault: {0}",
                                null == fe.Detail.InnerFault ? "No Inner Fault" : "Has Inner Fault");
                        }
                    }
                }
                // Additional exceptions to catch: SecurityTokenValidationException, ExpiredSecurityTokenException,
                // SecurityAccessDeniedException, MessageSecurityException, and SecurityNegotiationException.

                finally
                {
                    Console.WriteLine("Press <Enter> to exit.");
                    Console.ReadLine();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error while connecting to CRM " + ex.Message);
                Console.ReadKey();
            }
        }

        /// <summary>
        /// Gets a named connection string from App.config
        /// </summary>
        /// <param name="name">The name of the connection string to return</param>
        /// <returns>The named connection string</returns>
        public static string GetCRMConnectionString()
        {
            try
            {
                return ConfigurationManager.ConnectionStrings["CRMServer"].ConnectionString;
            }
            catch (Exception)
            {
                Console.WriteLine("You can set connection data in cds/App.config before running this sample. - Switching to Interactive Mode");
                return string.Empty;
            }
        }
    }
}