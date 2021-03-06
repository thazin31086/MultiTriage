using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace BugTriageModel.Models
{
    public class Ticket
    {
        public string ID { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string AssignedTo { get; set; }
        public string Status { get; set; }
        public string Type { get; set; }
    }
}