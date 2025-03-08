#!/bin/bash
# deploy-langgraph-agent.sh - Deploy LangGraph agents to Coolify

# Configuration - Update these values
COOLIFY_URL="http://5.78.72.45:8000"
API_KEY="ipKi4S78ov3aMAe0J6T5mItSQEPhCBqbwYD2r8Kje8706be2"
REPO_URL="https://github.com/yeondam88/test-agent"  # GitHub/GitLab repo containing your agent
BRANCH="main"
AGENT_NAME="Test LangGraph Agent"
AGENT_PORT=8000  # FastAPI will listen on this port

# Get CSRF token and cookies
echo "Getting CSRF token..."
RESPONSE=$(curl -s -c /tmp/coolify_cookies.txt $COOLIFY_URL/login)
CSRF_TOKEN=$(echo "$RESPONSE" | grep -o 'csrf-token" content="[^"]*"' | cut -d'"' -f3)

if [ -n "$CSRF_TOKEN" ]; then
  echo "Found CSRF token: ${CSRF_TOKEN:0:10}..."
  
  # Create application - using Docker deployment for LangGraph agent
  echo "Creating LangGraph agent application..."
  curl -X POST -s -b /tmp/coolify_cookies.txt \
    -H "X-CSRF-TOKEN: $CSRF_TOKEN" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"$AGENT_NAME\",
      \"git_repository\": \"$REPO_URL\",
      \"git_branch\": \"$BRANCH\",
      \"build_pack\": \"dockerfile\",
      \"port\": $AGENT_PORT,
      \"auto_deploy\": true,
      \"environment\": [
        {\"name\": \"OPENAI_API_KEY\", \"value\": \"YOUR_ACTUAL_OPENAI_API_KEY_HERE\"},
        {\"name\": \"HOST\", \"value\": \"0.0.0.0\"},
        {\"name\": \"PORT\", \"value\": \"$AGENT_PORT\"}
      ]
    }" \
    "$COOLIFY_URL/api/resources/applications"
    
  echo "Deployment initiated. Check Coolify dashboard for status."
  echo "Once deployed, your agent will be accessible at: http://your-coolify-instance/proxy/your-resource-id/"
  echo "Use this URL to connect LangGraph Studio to your agent."
else
  echo "Failed to get CSRF token."
fi 