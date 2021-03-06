using BugTriageModel.Models;
using BugTriageModel.Services;
using Swashbuckle.Swagger.Annotations;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using System.Web.Http;
using System.Web.Mvc;

namespace BugTriageModel.Controllers
{
    public class TicketController : ApiController
    {
        [SwaggerOperation("GetTickets")]
        public async Task<List<Ticket>> Get()
        {

            return await TicketService.GetTickets();
        }

        // POST api/<controller>
        public void Post([FromBody]string value)
        {
        }

        // PUT api/<controller>/5
        public void Put(int id, [FromBody]string value)
        {
        }

        // DELETE api/<controller>/5
        public void Delete(int id)
        {
        }
    }
}