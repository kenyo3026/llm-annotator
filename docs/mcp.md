# MCP (Model Context Protocol) Server Guide

## Overview

The LLM Annotator provides a Model Context Protocol (MCP) server implementation using [FastMCP](https://github.com/jlowin/fastmcp), enabling seamless integration with MCP-compatible clients like Cursor, Claude Desktop, and Cline (formerly known as drowcoder).

### What is MCP?

Model Context Protocol (MCP) is an open standard developed by Anthropic that enables AI assistants to connect with external tools, services, and data sources. It provides a standardized way for AI models to:

- Access external APIs and services
- Execute tools and functions
- Read resources from various sources
- Integrate with development environments

## Architecture

The MCP server exposes three main types of capabilities:

### 1. Tools
Functions that can be called by the AI (requires user approval):
- **`annotate`**: Annotate text with tags using LLM-based classification

### 2. Resources
Data accessible to clients:
- **`annotator://annotators`**: List all available annotators
- **`annotator://models`**: List all available models

### 3. Prompts
Pre-written templates for specific tasks (currently not implemented)

## Starting the MCP Server

### Installation

First, install the package with all dependencies:

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

This will install the `annotator-mcp` command-line tool.

### Server Modes

The MCP server supports two transport protocols:

#### 1. stdio (Local Mode)
Direct communication via standard input/output. Recommended for local tools like Cursor and Claude Desktop.

```bash
annotator-mcp --transport stdio
```

**Use cases:**
- Single user
- Local development
- Auto-managed by client (Cursor/Claude Desktop)

#### 2. streamable-http (Remote Mode)
Network-based communication for remote deployment.

```bash
annotator-mcp --transport streamable-http --host 0.0.0.0 --port 8001
```

**Use cases:**
- Multi-user environments
- Remote servers
- HTTP-based integrations

### Command-Line Options

```bash
annotator-mcp [OPTIONS]

Options:
  -c, --config PATH           Path to configuration file
                              (default: configs/config.yaml)

  --transport {stdio|streamable-http}
                              Transport protocol to use
                              (default: stdio)

  --host HOST                 Host to bind to for streamable-http
                              (default: 0.0.0.0)

  --port PORT                 Port to bind to for streamable-http
                              (default: 8001)

  --path PATH                 Path for streamable-http endpoint
                              (default: /mcp)
```

### Examples

**Run with default config (stdio):**
```bash
annotator-mcp
```

**Run with custom config:**
```bash
annotator-mcp -c configs/custom.yaml --transport stdio
```

**Run as HTTP server:**
```bash
annotator-mcp --transport streamable-http --port 8001
```

## Client Configuration

### Cursor IDE

#### Configuration File Location

- **Global** (all projects): `~/.cursor/mcp.json`
- **Project-specific**: `.cursor/mcp.json` in your project root

#### Setup Steps

1. Open Cursor Settings:
   - macOS: `Cmd+Shift+J`
   - Windows/Linux: `Ctrl+Shift+J`

2. Navigate to: **Tools & Integrations** → **Model Context Protocol**

3. Click **"New MCP Servers"** to create/edit `mcp.json`

4. Add the following configuration:

<details open>
<summary>JSON Format</summary>

```json
{
  "mcpServers": {
    "llm-annotator": {
      "command": "/path/to/your/venv/bin/annotator-mcp",
      "args": [
        "--transport",
        "stdio",
        "-c",
        "/path/to/your/configs/config.yaml"
      ],
      "env": {}
    }
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
mcpServers:
  llm-annotator:
    command: /path/to/your/venv/bin/annotator-mcp
    args:
      - --transport
      - stdio
      - -c
      - /path/to/your/configs/config.yaml
    env: {}
```

</details>

#### Finding the Correct Paths

**For virtual environment path:**
```bash
# Activate your virtual environment first
source .venv/bin/activate  # or your venv path

# Find the annotator-mcp command path
which annotator-mcp
# Output: /path/to/your/venv/bin/annotator-mcp
```

**For config file path:**
```bash
# Use absolute path to your config file
pwd
# If you're in project root, append /configs/config.yaml
```

#### Complete Example

Assuming:
- Project path: `/Users/username/projects/llm-annotator`
- Virtual environment: `.venv` in project root

<details open>
<summary>JSON Format</summary>

```json
{
  "mcpServers": {
    "llm-annotator": {
      "command": "/Users/username/projects/llm-annotator/.venv/bin/annotator-mcp",
      "args": [
        "--transport",
        "stdio",
        "-c",
        "/Users/username/projects/llm-annotator/configs/config.yaml"
      ],
      "env": {}
    }
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
mcpServers:
  llm-annotator:
    command: /Users/username/projects/llm-annotator/.venv/bin/annotator-mcp
    args:
      - --transport
      - stdio
      - -c
      - /Users/username/projects/llm-annotator/configs/config.yaml
    env: {}
```

</details>

### Cline (formerly drowcoder)

Cline uses the same MCP configuration format as Cursor.

#### Configuration File Location

- **VS Code Settings**: Follow VS Code MCP extension configuration
- **Standalone**: Check Cline's documentation for specific config path

#### Configuration Format

Same as Cursor configuration above. Cline follows the standard MCP client configuration:

<details open>
<summary>JSON Format</summary>

```json
{
  "mcpServers": {
    "llm-annotator": {
      "command": "/absolute/path/to/annotator-mcp",
      "args": ["--transport", "stdio", "-c", "/absolute/path/to/config.yaml"],
      "env": {}
    }
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
mcpServers:
  llm-annotator:
    command: /absolute/path/to/annotator-mcp
    args:
      - --transport
      - stdio
      - -c
      - /absolute/path/to/config.yaml
    env: {}
```

</details>

### Claude Desktop

Claude Desktop also supports MCP servers using stdio transport.

#### Configuration File Location

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Configuration Format

<details open>
<summary>JSON Format</summary>

```json
{
  "mcpServers": {
    "llm-annotator": {
      "command": "/path/to/venv/bin/annotator-mcp",
      "args": [
        "--transport",
        "stdio",
        "-c",
        "/path/to/config.yaml"
      ]
    }
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
mcpServers:
  llm-annotator:
    command: /path/to/venv/bin/annotator-mcp
    args:
      - --transport
      - stdio
      - -c
      - /path/to/config.yaml
```

</details>

### Remote Server Configuration

For streamable-http transport (remote servers):

<details open>
<summary>JSON Format</summary>

```json
{
  "mcpServers": {
    "llm-annotator-remote": {
      "url": "http://your-server.com:8001/mcp"
    }
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
mcpServers:
  llm-annotator-remote:
    url: http://your-server.com:8001/mcp
```

</details>

## Configuration Parameters

### Required Parameters

- **`command`**: Executable command (python, node, or direct path to binary)
- **`args`**: Array of command-line arguments

### Optional Parameters

- **`env`**: Environment variables (useful for API keys or sensitive data)
- **`url`**: Remote server URL (for streamable-http transport)

### Environment Variables

You can pass environment variables through the `env` field:

<details open>
<summary>JSON Format</summary>

```json
{
  "mcpServers": {
    "llm-annotator": {
      "command": "/path/to/annotator-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "API_KEY": "your-api-key",
        "DEBUG": "true"
      }
    }
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
mcpServers:
  llm-annotator:
    command: /path/to/annotator-mcp
    args:
      - --transport
      - stdio
    env:
      API_KEY: your-api-key
      DEBUG: "true"
```

</details>

## Available Tools

### `annotate`

Annotate text with tags using LLM-based classification.

**Parameters:**
- `context` (string, required): Text to annotate
- `annotator` (string, optional): Annotator name to use (default: first annotator in config)
- `model` (string, optional): Model name to use (default: first model in config)

**Returns:**

<details open>
<summary>JSON Format</summary>

```json
{
  "tags": ["tag1", "tag2"],
  "status": "success",
  "metadata": {
    "model": "gemini-flash",
    "annotator": "stock-chat-tagging",
    "latency": 1.23
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
tags:
  - tag1
  - tag2
status: success
metadata:
  model: gemini-flash
  annotator: stock-chat-tagging
  latency: 1.23
```

</details>

**Example usage in Cursor:**
```
Ask the AI: "Use the annotate tool to tag this text: 'Tesla stock surged 10% today'"
```

## Available Resources

### `annotator://annotators`

List all available annotators defined in your configuration.

**Returns:**

<details open>
<summary>JSON Format</summary>

```json
{
  "annotators": ["open-tagging", "stock-chat-tagging"]
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
annotators:
  - open-tagging
  - stock-chat-tagging
```

</details>

### `annotator://models`

List all available models defined in your configuration.

**Returns:**

<details open>
<summary>JSON Format</summary>

```json
{
  "models": ["gemini-flash", "gpt-4"]
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
models:
  - gemini-flash
  - gpt-4
```

</details>

## Troubleshooting

### Server Won't Start

1. **Check command path:**
   ```bash
   which annotator-mcp
   ```
   Make sure the path in your config matches the output.

2. **Check config file:**
   ```bash
   cat /path/to/config.yaml
   ```
   Verify the config file exists and is valid YAML.

3. **Test manual execution:**
   ```bash
   /path/to/annotator-mcp --transport stdio -c /path/to/config.yaml
   ```
   Should start without errors (Ctrl+C to exit).

### Connection Errors

1. **Check MCP logs:**
   - Cursor: **View** → **Output** → **MCP Logs**

2. **Verify JSON syntax:**
   Use a JSON validator to check your `mcp.json` file.

3. **Restart client:**
   After configuration changes, restart Cursor/Claude Desktop.

### Tool Not Available

1. **Check server status:**
   - Cursor: Green indicator = running, Red = failed

2. **Verify configuration:**
   - Ensure `command` path is absolute
   - Ensure `args` array is properly formatted
   - Check that config file path in `args` is correct

### Permission Issues

If you get permission denied errors:

```bash
# Make sure the command is executable
chmod +x /path/to/venv/bin/annotator-mcp
```

## Best Practices

### 1. Use Absolute Paths

Always use absolute paths in MCP configuration:

<details open>
<summary>JSON Format</summary>

```json
{
  "command": "/absolute/path/to/annotator-mcp",
  "args": ["-c", "/absolute/path/to/config.yaml"]
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
command: /absolute/path/to/annotator-mcp
args:
  - -c
  - /absolute/path/to/config.yaml
```

</details>

### 2. Environment Variables for Secrets

Don't hardcode API keys in config files:

<details open>
<summary>JSON Format</summary>

```json
{
  "env": {
    "GEMINI_API_KEY": "your-key-here"
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
env:
  GEMINI_API_KEY: your-key-here
```

</details>

Then reference in your `config.yaml`:
```yaml
models:
  - name: gemini-flash
    model: gemini/gemini-2.5-flash
    api_key: ${GEMINI_API_KEY}
```

### 3. Test Before Integration

Test the MCP server manually before adding to client:

```bash
# Test stdio mode
annotator-mcp --transport stdio -c configs/config.yaml

# Test HTTP mode
annotator-mcp --transport streamable-http --port 8001
```

### 4. Version Control

Add to `.gitignore`:
```
.cursor/mcp.json
```

Provide an example file:
```
mcp-client-config.example.json
```

### 5. Multiple Environments

Use different config files for different environments:

<details open>
<summary>JSON Format</summary>

```json
{
  "llm-annotator-dev": {
    "command": "/path/to/annotator-mcp",
    "args": ["-c", "/path/to/configs/dev.yaml"]
  },
  "llm-annotator-prod": {
    "command": "/path/to/annotator-mcp",
    "args": ["-c", "/path/to/configs/prod.yaml"]
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
llm-annotator-dev:
  command: /path/to/annotator-mcp
  args:
    - -c
    - /path/to/configs/dev.yaml
llm-annotator-prod:
  command: /path/to/annotator-mcp
  args:
    - -c
    - /path/to/configs/prod.yaml
```

</details>

## Advanced Usage

### Custom Transport Configuration

For advanced HTTP configurations:

```bash
annotator-mcp \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8001 \
  --path /api/mcp \
  -c configs/config.yaml
```

### Running as a Service

Create a systemd service file (`/etc/systemd/system/annotator-mcp.service`):

```ini
[Unit]
Description=LLM Annotator MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/annotator-mcp --transport streamable-http --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable annotator-mcp
sudo systemctl start annotator-mcp
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8001

CMD ["annotator-mcp", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8001"]
```

Build and run:
```bash
docker build -t llm-annotator-mcp .
docker run -p 8001:8001 -v $(pwd)/configs:/app/configs llm-annotator-mcp
```

## Security Considerations

### 1. API Keys

Never commit API keys to version control:
- Use environment variables
- Use `.env` files (add to `.gitignore`)
- Use secret management services (AWS Secrets Manager, HashiCorp Vault)

### 2. Network Security

For remote servers:
- Use HTTPS/TLS encryption
- Implement authentication/authorization
- Use firewall rules to restrict access
- Consider VPN for sensitive deployments

### 3. Input Validation

The MCP server includes basic input validation, but always:
- Sanitize user inputs
- Set rate limits
- Monitor for abuse
- Log suspicious activities

### 4. Code Review

When using third-party MCP servers:
- Review the source code
- Check for security vulnerabilities
- Verify dependencies
- Monitor for updates

## Resources

### Official Documentation

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Cursor MCP Guide](https://docs.cursor.com/context/model-context-protocol)

### Community

- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Cursor Community](https://forum.cursor.com/)

### Related Tools

- **Claude Desktop**: Native MCP support
- **Cursor**: IDE with MCP integration
- **Cline**: VS Code extension with MCP support
- **Continue**: Open-source coding assistant with MCP

## FAQ

### Q: What's the difference between stdio and streamable-http?

**A:**
- **stdio**: Direct process communication, auto-managed by client, single user
- **streamable-http**: Network-based, manually managed, supports multiple users

### Q: Can I use multiple MCP servers?

**A:** Yes! Add multiple entries to your `mcpServers` config:

<details open>
<summary>JSON Format</summary>

```json
{
  "mcpServers": {
    "llm-annotator": { ... },
    "another-server": { ... }
  }
}
```

</details>

<details>
<summary>YAML Format</summary>

```yaml
mcpServers:
  llm-annotator: { ... }
  another-server: { ... }
```

</details>

### Q: How do I debug MCP communication?

**A:**
1. Check MCP logs in Cursor (View → Output → MCP Logs)
2. Run the server manually to see output
3. Add logging to your server code
4. Use `DEBUG=true` environment variable

### Q: Can I use this with other AI clients?

**A:** Yes! Any client that supports the Model Context Protocol can use this server. This includes:
- Claude Desktop
- Cursor
- Cline (drowcoder)
- Continue
- Custom MCP clients

### Q: How do I update the MCP server?

**A:**
```bash
# Pull latest changes
git pull

# Reinstall
uv pip install -e .

# Restart the client (Cursor/Claude Desktop)
```

### Q: What if my config file changes?

**A:** The MCP server loads configuration on startup. To apply changes:
1. Update your `config.yaml`
2. Restart the MCP server (or restart Cursor/Claude Desktop)

## Contributing

Found a bug or want to contribute? Check out our [GitHub repository](https://github.com/yourusername/llm-annotator) and submit an issue or pull request!

## License

See the main project LICENSE file for details.
