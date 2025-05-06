import { useEffect, useState } from "react";
import { useAppSelector } from "../store/hooks";
import "./progress-panel.css";
import {
  BeakerIcon,
  AcademicCapIcon,
  UserIcon,
  PencilIcon,
  // DocumentArrowUpIcon,
  MegaphoneIcon,
} from "@heroicons/react/24/outline";
import { CheckCircleIcon } from "@heroicons/react/24/solid";

// Define agent types and their statuses
interface AgentStatus {
  name: string;
  icon: JSX.Element;
  color: string;
  status: "waiting" | "active" | "completed";
  description: string;
  progress: number; // Track individual agent progress 0-100%
  lastMessage?: string; // Store the latest message from this agent
}

export const ProgressPanel = () => {
  const messages = useAppSelector((state) => state.message);
  const [overallProgress, setOverallProgress] = useState(0);
  const [showPanel, setShowPanel] = useState(false);

  // Initialize agent statuses
  const [agents, setAgents] = useState<AgentStatus[]>([
    {
      name: "Researcher",
      icon: <BeakerIcon className="w-6 h-6" />,
      color: "text-sky-600 border-sky-600",
      status: "waiting",
      description: "Gathering information and research data",
      progress: 0,
      lastMessage: ""
    },
    {
      name: "Marketing",
      icon: <AcademicCapIcon className="w-6 h-6" />,
      color: "text-green-600 border-green-600",
      status: "waiting",
      description: "Analyzing market trends and positioning",
      progress: 0,
      lastMessage: ""
    },
    {
      name: "Writer",
      icon: <UserIcon className="w-6 h-6" />,
      color: "text-violet-600 border-violet-600",
      status: "waiting",
      description: "Creating engaging content",
      progress: 0,
      lastMessage: ""
    },
    {
      name: "Editor",
      icon: <PencilIcon className="w-6 h-6" />,
      color: "text-amber-600 border-amber-600",
      status: "waiting",
      description: "Refining and polishing content",
      progress: 0,
      lastMessage: ""
    },
    {
      name: "Influencer",
      icon: <MegaphoneIcon className="w-6 h-6" />,
      color: "text-sky-600 border-sky-600",
      status: "waiting",
      description: "Generating social media content for distribution",
      progress: 0,
      lastMessage: ""
    }
  ]);

  // Always show the panel in this implementation
  useEffect(() => {
    setShowPanel(true);
  }, []);

  // Update agent statuses based on messages
  useEffect(() => {
    if (messages.length === 0) return;

    // Create a new copy of agents to update
    const updatedAgents = [...agents];
    
    // Track agent activities
    const agentActivity = {
      researcher: { seen: false, completed: false, messageCount: 0, lastMessage: "" },
      marketing: { seen: false, completed: false, messageCount: 0, lastMessage: "" },
      writer: { seen: false, completed: false, messageCount: 0, lastMessage: "" },
      editor: { seen: false, completed: false, messageCount: 0, lastMessage: "" },
      publishing: { seen: false, completed: false, messageCount: 0, lastMessage: "" },
      influencer: { seen: false, completed: false, messageCount: 0, lastMessage: "" }
    };
    
    // Process each message to update agent statuses
    messages.forEach(message => {
      const agentType = message.type;
      const msg = message.message.toLowerCase();
      
      // Only process messages from known agent types
      if (!(agentType in agentActivity)) return;
      
      const agentKey = agentType as keyof typeof agentActivity;
      
      // Update agent activity tracking
      agentActivity[agentKey].seen = true;
      agentActivity[agentKey].messageCount++;
      agentActivity[agentKey].lastMessage = message.message;
      
      // Check for progress indicators in message
      const progressMatch = msg.match(/(\d+)%|progress: (\d+)/i);
      if (progressMatch) {
        const progressValue = parseInt(progressMatch[1] || progressMatch[2], 10);
        if (!isNaN(progressValue) && progressValue >= 0 && progressValue <= 100) {
          const agentIndex = getAgentIndexByType(agentType);
          if (agentIndex >= 0) {
            updatedAgents[agentIndex].progress = progressValue;
          }
        }
      }
      
      // Check for completion terms
      const isCompletionMessage = 
        msg.includes("complete") || 
        msg.includes("finish") || 
        msg.includes("done") || 
        msg.includes("completed") ||
        msg.includes("published") ||
        msg.includes("created") ||
        msg.includes("ready") && msg.includes("next");
        
      if (isCompletionMessage) {
        agentActivity[agentKey].completed = true;
      }
    });
    
    // Helper function to map agent type to array index
    function getAgentIndexByType(type: string): number {
      switch(type) {
        case "researcher": return 0;
        case "marketing": return 1;
        case "writer": return 2;
        case "editor": return 3;
        case "publishing": 
        case "influencer": return 4;
        default: return -1;
      }
    }
    
    // Update agent statuses and progress based on activity
    Object.entries(agentActivity).forEach(([type, activity]) => {
      const agentIndex = getAgentIndexByType(type);
      if (agentIndex >= 0) {
        // Update status
        if (activity.completed) {
          updatedAgents[agentIndex].status = "completed";
          updatedAgents[agentIndex].progress = 100;
        } else if (activity.seen) {
          updatedAgents[agentIndex].status = "active";
          
          // If progress hasn't been explicitly set, estimate based on message count
          if (updatedAgents[agentIndex].progress === 0) {
            // Assume each message represents some progress, up to 90% (reserve 100% for completion)
            const estimatedProgress = Math.min(90, activity.messageCount * 15);
            updatedAgents[agentIndex].progress = estimatedProgress;
          }
        }
        
        // Update last message
        if (activity.lastMessage) {
          updatedAgents[agentIndex].lastMessage = activity.lastMessage;
        }
      }
    });
    
    // Special case for social media influencer affecting publishing agent
    if (agentActivity.influencer.completed) {
      updatedAgents[4].status = "completed";
      updatedAgents[4].progress = 100;
    }
    
    // Count completed agents for overall progress
    let completed = 0;
    updatedAgents.forEach(agent => {
      if (agent.status === "completed") completed++;
    });

    // Update overall progress
    setOverallProgress(Math.round((completed / updatedAgents.length) * 100));
    setAgents(updatedAgents);
    
    // Reset progress if a new content generation starts
    const latestMessages = messages.slice(-3);
    const hasStartMessage = latestMessages.some(m => 
      m.type === "message" && 
      (m.message.includes("Starting content creation") || m.message.includes("Planning content creation"))
    );
    
    if (hasStartMessage && overallProgress > 0) {
      // Reset with a brief delay for visual effect
      setTimeout(() => {
        const resetAgents = updatedAgents.map(agent => ({
          ...agent,
          status: "waiting" as const,
          progress: 0,
          lastMessage: ""
        }));
        setAgents(resetAgents);
        setOverallProgress(0);
      }, 500);
    }
  }, [messages, agents, overallProgress]);

  if (!showPanel) return null;

  return (
    <div className="w-full bg-white rounded-lg shadow-md p-6 mb-6 border-t-4 border-blue-400 fade-in-up">
      <h3 className="text-lg font-medium text-blue-800 mb-3 flex items-center justify-between">
        <div className="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Content Generation Progress
        </div>
        <span className="text-sm font-normal bg-blue-100 text-blue-800 py-1 px-3 rounded-full">
          {overallProgress}% Complete
        </span>
      </h3>
      
      {/* Progress bar */}
      <div className="w-full bg-gray-100 rounded-full h-2.5 mb-6 overflow-hidden shadow-inner">
        <div 
          className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2.5 rounded-full transition-all duration-500 ease-in-out progress-bar" 
          style={{ width: `${overallProgress}%` }}
        ></div>
      </div>
      
      {/* Agent status display */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {agents.map((agent, index) => (
          <div 
            key={index} 
            className={`p-4 rounded-lg border shadow agent-card ${
              agent.status === "active" 
                ? "bg-blue-50 border-blue-200 agent-pulse" 
                : agent.status === "completed" 
                  ? "bg-green-50 border-green-200 completed" 
                  : "bg-gray-50 border-gray-200"
            } transition-all duration-300 hover:shadow-md`}
          >
            <div className="flex items-center mb-3">
              <div className={`${agent.color} agent-icon p-2 rounded-full bg-opacity-20 ${agent.color.replace('text', 'bg').replace('border', 'bg')}`}>
                {agent.icon}
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-semibold">{agent.name}</p>
                <div className="flex items-center mt-1">
                  {agent.status === "completed" ? (
                    <span className="inline-flex items-center text-xs text-green-600">
                      <CheckCircleIcon className="w-3 h-3 mr-1" />
                      Complete
                    </span>
                  ) : agent.status === "active" ? (
                    <span className="inline-flex items-center text-xs text-blue-600">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-1 animate-pulse"></div>
                      Active
                    </span>
                  ) : (
                    <span className="text-xs text-gray-500">Waiting...</span>
                  )}
                </div>
              </div>
            </div>
            
            {/* Agent progress bar */}
            <div className="w-full bg-gray-100 rounded-full h-1.5 mb-2">
              <div 
                className={`h-1.5 rounded-full transition-all duration-300 ${
                  agent.status === "completed" 
                    ? "bg-green-500" 
                    : agent.status === "active" 
                      ? "bg-blue-500" 
                      : "bg-gray-300"
                }`}
                style={{ width: `${agent.progress}%` }}
              ></div>
            </div>
            
            {/* Agent description or latest message */}
            <p className="text-xs text-gray-600 mt-2 line-clamp-2 h-8">
              {agent.status !== "waiting" && agent.lastMessage 
                ? agent.lastMessage 
                : agent.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressPanel;
