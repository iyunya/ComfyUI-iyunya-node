import { app } from "../../scripts/app.js";

// 主菜单项及下拉菜单
class IyunyaNodesMenu {
  constructor() {
    // 保留简化版的构造函数，移除不需要的菜单项数组
  }

  // 添加对话框外部点击关闭和ESC键关闭功能
  setupDialogCloseEvents(dialog, onClose) {
    // 点击对话框外部区域关闭
    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) {
        if (typeof onClose === 'function') {
          onClose(false);
        }
        document.body.removeChild(dialog);
      }
    });
    
    // ESC键关闭
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        if (typeof onClose === 'function') {
          onClose(false);
        }
        document.body.removeChild(dialog);
        document.removeEventListener('keydown', handleKeyDown);
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    
    // 返回清理函数
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }

  // 自定义 alert 对话框
  showAlert(message, title = "提示") {
    return new Promise((resolve) => {
      // 创建对话框DOM元素
      const dialog = document.createElement("div");
      dialog.className = "iyunya-dialog";
      dialog.innerHTML = `
        <div class="iyunya-dialog-content iyunya-dialog-small">
          <div class="iyunya-dialog-header">
            <h3>${title}</h3>
            <button class="iyunya-dialog-close">&times;</button>
          </div>
          <div class="iyunya-dialog-body">
            <div class="iyunya-message">${message}</div>
          </div>
          <div class="iyunya-dialog-footer">
            <button id="alert-confirm-btn" class="iyunya-btn iyunya-btn-primary">确定</button>
          </div>
        </div>
      `;
      
      // 添加对话框样式
      this.addDialogStyles();
      
      // 将对话框添加到文档
      document.body.appendChild(dialog);
      
      // 关闭按钮事件
      dialog.querySelector(".iyunya-dialog-close").onclick = () => {
        document.body.removeChild(dialog);
        resolve(true);
      };
      
      // 确认按钮事件
      dialog.querySelector("#alert-confirm-btn").onclick = () => {
        document.body.removeChild(dialog);
        resolve(true);
      };
      
      // 添加对话框外部点击和ESC关闭
      this.setupDialogCloseEvents(dialog, resolve);
    });
  }
  
  // 自定义节点创建成功对话框
  showNodeCreatedAlert(nodeName) {
    return new Promise((resolve) => {
      // 创建对话框DOM元素
      const dialog = document.createElement("div");
      dialog.className = "iyunya-dialog";
      dialog.innerHTML = `
        <div class="iyunya-dialog-content iyunya-dialog-small">
          <div class="iyunya-dialog-header">
            <h3>创建成功</h3>
            <button class="iyunya-dialog-close">&times;</button>
          </div>
          <div class="iyunya-dialog-body">
            <div class="iyunya-message">
              <p>节点 "${nodeName}" 创建成功!</p>
              <p class="iyunya-note">注意：需要刷新页面后才能在节点列表中选择到新创建的节点。</p>
            </div>
          </div>
          <div class="iyunya-dialog-footer">
            <button id="refresh-later-btn" class="iyunya-btn">稍后刷新</button>
            <button id="refresh-now-btn" class="iyunya-btn iyunya-btn-primary">立即刷新</button>
          </div>
        </div>
      `;
      
      // 添加对话框样式
      this.addDialogStyles();
      
      // 将对话框添加到文档
      document.body.appendChild(dialog);
      
      // 关闭按钮事件
      dialog.querySelector(".iyunya-dialog-close").onclick = () => {
        document.body.removeChild(dialog);
        resolve(false); // 不刷新
      };
      
      // 稍后刷新按钮事件
      dialog.querySelector("#refresh-later-btn").onclick = () => {
        document.body.removeChild(dialog);
        resolve(false); // 不刷新
      };
      
      // 立即刷新按钮事件
      dialog.querySelector("#refresh-now-btn").onclick = () => {
        document.body.removeChild(dialog);
        resolve(true); // 立即刷新
      };
      
      // 添加对话框外部点击和ESC关闭
      this.setupDialogCloseEvents(dialog, resolve);
    });
  }
  
  // 自定义 confirm 对话框
  showConfirm(message, title = "确认") {
    return new Promise((resolve) => {
      // 创建对话框DOM元素
      const dialog = document.createElement("div");
      dialog.className = "iyunya-dialog";
      dialog.innerHTML = `
        <div class="iyunya-dialog-content iyunya-dialog-small">
          <div class="iyunya-dialog-header">
            <h3>${title}</h3>
            <button class="iyunya-dialog-close">&times;</button>
          </div>
          <div class="iyunya-dialog-body">
            <div class="iyunya-message">${message}</div>
          </div>
          <div class="iyunya-dialog-footer">
            <button id="confirm-cancel-btn" class="iyunya-btn">取消</button>
            <button id="confirm-ok-btn" class="iyunya-btn iyunya-btn-primary">确定</button>
          </div>
        </div>
      `;
      
      // 添加对话框样式
      this.addDialogStyles();
      
      // 将对话框添加到文档
      document.body.appendChild(dialog);
      
      // 关闭按钮事件
      dialog.querySelector(".iyunya-dialog-close").onclick = () => {
        document.body.removeChild(dialog);
        resolve(false);
      };
      
      // 取消按钮事件
      dialog.querySelector("#confirm-cancel-btn").onclick = () => {
        document.body.removeChild(dialog);
        resolve(false);
      };
      
      // 确认按钮事件
      dialog.querySelector("#confirm-ok-btn").onclick = () => {
        document.body.removeChild(dialog);
        resolve(true);
      };
      
      // 添加对话框外部点击和ESC关闭
      this.setupDialogCloseEvents(dialog, resolve);
    });
  }

  // 显示创建节点的对话框
  showCreateNodeDialog(nodeType = "in") {
    // 创建对话框DOM元素
    const dialog = document.createElement("div");
    dialog.className = "iyunya-dialog";
    dialog.innerHTML = `
      <div class="iyunya-dialog-content">
        <div class="iyunya-dialog-header">
          <h3>创建新${nodeType === "in" ? "输入" : "输出"}节点</h3>
          <button class="iyunya-dialog-close">&times;</button>
        </div>
        <div class="iyunya-dialog-body">
          <div class="iyunya-form-group">
            <label>节点基本信息</label>
            <div class="node-info-row">
              <div class="node-name-container">
                <label for="node-name">展示名称</label>
                <input type="text" id="node-name" placeholder="请输入节点名称" />
              </div>
              <div class="node-id-container">
                <label for="node-id">节点ID (可选)</label>
                <input type="text" id="node-id" placeholder="可选，节点ID" />
              </div>
            </div>
          </div>
          <div class="iyunya-form-group">
            <label>节点${nodeType === "in" ? "输入" : "输出"}参数</label>
            <div id="input-params-container">
              <div class="input-param-row">
                <input type="text" class="param-name" placeholder="参数名称" />
                <select class="param-type">
                  <option value="STRING">文本 (STRING)</option>
                  <option value="INT">整数 (INT)</option>
                  <option value="FLOAT">浮点数 (FLOAT)</option>
                  <option value="BOOLEAN">布尔值 (BOOLEAN)</option>
                </select>
                <button class="remove-param">删除</button>
              </div>
            </div>
            <button id="add-param-btn" class="iyunya-btn">添加参数</button>
          </div>
        </div>
        <div class="iyunya-dialog-footer">
          <input type="hidden" id="node-type" value="${nodeType}" />
          <button id="create-node-btn" class="iyunya-btn iyunya-btn-primary">创建节点</button>
          <button id="cancel-btn" class="iyunya-btn">取消</button>
        </div>
      </div>
    `;
    
    // 添加对话框样式
    this.addDialogStyles();
    
    // 将对话框添加到文档
    document.body.appendChild(dialog);
    
    // 添加事件处理
    dialog.querySelector(".iyunya-dialog-close").onclick = () => {
      document.body.removeChild(dialog);
    };
    
    dialog.querySelector("#cancel-btn").onclick = () => {
      document.body.removeChild(dialog);
    };
    
    // 添加参数按钮
    dialog.querySelector("#add-param-btn").onclick = () => {
      const container = dialog.querySelector("#input-params-container");
      const newRow = document.createElement("div");
      newRow.className = "input-param-row";
      newRow.innerHTML = `
        <input type="text" class="param-name" placeholder="参数名称" />
        <select class="param-type">
          <option value="STRING">文本 (STRING)</option>
          <option value="INT">整数 (INT)</option>
          <option value="FLOAT">浮点数 (FLOAT)</option>
          <option value="BOOLEAN">布尔值 (BOOLEAN)</option>
        </select>
        <button class="remove-param">删除</button>
      `;
      
      container.appendChild(newRow);
      
      // 为删除按钮添加事件
      newRow.querySelector(".remove-param").onclick = (e) => {
        container.removeChild(newRow);
      };
    };
    
    // 为已有的删除按钮添加事件
    dialog.querySelectorAll(".remove-param").forEach(btn => {
      btn.onclick = (e) => {
        const row = e.target.closest(".input-param-row");
        if (row && row.parentElement.children.length > 1) {
          row.parentElement.removeChild(row);
        }
      };
    });
    
    // 创建节点按钮
    dialog.querySelector("#create-node-btn").onclick = () => {
      const nodeName = dialog.querySelector("#node-name").value.trim();
      const nodeId = dialog.querySelector("#node-id").value.trim();
      const nodeType = dialog.querySelector("#node-type").value;
      
      if (!nodeName) {
        this.showAlert("请输入节点名称");
        return;
      }
      
      const inputs = {};
      let hasError = false;
      
      dialog.querySelectorAll(".input-param-row").forEach(row => {
        const paramName = row.querySelector(".param-name").value.trim();
        const paramType = row.querySelector(".param-type").value;
        
        if (!paramName) {
          this.showAlert("参数名称不能为空");
          hasError = true;
          return;
        }
        
        inputs[paramName] = paramType;
      });
      
      if (hasError) return;
      
      if (Object.keys(inputs).length === 0) {
        this.showAlert("请至少添加一个参数");
        return;
      }
      
      // 发送API请求创建节点
      this.createNode(nodeName, inputs, dialog, nodeId, nodeType);
    };
    
    // 添加对话框外部点击和ESC关闭
    this.setupDialogCloseEvents(dialog);
  }
  
  // 显示节点管理对话框
  async showManageNodesDialog() {
    try {
      // 获取所有节点列表
      const response = await fetch("/api/iyunya/node/list");
      const result = await response.json();
      
      if (result.status !== "success") {
        throw new Error(result.message || "获取节点列表失败");
      }
      
      const nodes = result.nodes || [];
      
      // 分离输入和输出节点
      const inNodes = nodes.filter(node => node.group === "in");
      const outNodes = nodes.filter(node => node.group === "out");
      
      // 创建对话框DOM元素
      const dialog = document.createElement("div");
      dialog.className = "iyunya-dialog";
      dialog.innerHTML = `
        <div class="iyunya-dialog-content iyunya-dialog-large">
          <div class="iyunya-dialog-header">
            <h3>管理动态节点</h3>
            <button class="iyunya-dialog-close">&times;</button>
          </div>
          <div class="iyunya-dialog-body">
            <div class="iyunya-tabs">
              <div class="iyunya-tab-buttons">
                <button class="iyunya-tab-btn active" data-tab="in">输入节点</button>
                <button class="iyunya-tab-btn" data-tab="out">输出节点</button>
              </div>
              
              <div class="iyunya-tab-content active" id="tab-in">
                <div class="iyunya-nodes-controls" style="margin-bottom: 20px;">
                  <button id="create-in-node-btn" class="iyunya-btn iyunya-btn-primary">创建新输入节点</button>
                </div>
                <div class="iyunya-nodes-list">
                  <table class="iyunya-table">
                    <thead>
                      <tr>
                        <th>展示名称</th>
                        <th>类型</th>
                        <th>参数个数</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${inNodes.length > 0 ? 
                        inNodes.map(node => `
                          <tr data-node-id="${node.id}" data-node-group="${node.group}">
                            <td>${node.display_name}</td>
                            <td>${node.node_name}</td>
                            <td>${node.return_names ? node.return_names.length : 0}</td>
                            <td>
                              <button class="iyunya-btn iyunya-btn-small iyunya-btn-danger delete-node-btn">删除</button>
                            </td>
                          </tr>
                        `).join("") : 
                        '<tr><td colspan="4" class="empty-list">没有创建任何输入节点</td></tr>'
                      }
                    </tbody>
                  </table>
                </div>
              </div>
              
              <div class="iyunya-tab-content" id="tab-out">
                <div class="iyunya-nodes-controls" style="margin-bottom: 20px;">
                  <button id="create-out-node-btn" class="iyunya-btn iyunya-btn-primary">创建新输出节点</button>
                </div>
                <div class="iyunya-nodes-list">
                  <table class="iyunya-table">
                    <thead>
                      <tr>
                        <th>展示名称</th>
                        <th>类型</th>
                        <th>参数个数</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${outNodes.length > 0 ? 
                        outNodes.map(node => `
                          <tr data-node-id="${node.id}" data-node-group="${node.group}">
                            <td>${node.display_name}</td>
                            <td>${node.node_name}</td>
                            <td>${node.return_names ? node.return_names.length : 0}</td>
                            <td>
                              <button class="iyunya-btn iyunya-btn-small iyunya-btn-danger delete-node-btn">删除</button>
                            </td>
                          </tr>
                        `).join("") : 
                        '<tr><td colspan="4" class="empty-list">没有创建任何输出节点</td></tr>'
                      }
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="iyunya-dialog-footer">
            <button id="refresh-nodes-btn" class="iyunya-btn">刷新列表</button>
            <button id="close-btn" class="iyunya-btn">关闭</button>
          </div>
        </div>
      `;
      
      // 添加对话框样式
      this.addDialogStyles();
      
      // 将对话框添加到文档
      document.body.appendChild(dialog);
      
      // 添加事件处理
      dialog.querySelector(".iyunya-dialog-close").onclick = () => {
        document.body.removeChild(dialog);
      };
      
      dialog.querySelector("#close-btn").onclick = () => {
        document.body.removeChild(dialog);
      };
      
      // Tab切换逻辑
      dialog.querySelectorAll(".iyunya-tab-btn").forEach(btn => {
        btn.onclick = () => {
          // 移除所有活动状态
          dialog.querySelectorAll(".iyunya-tab-btn").forEach(b => b.classList.remove("active"));
          dialog.querySelectorAll(".iyunya-tab-content").forEach(c => c.classList.remove("active"));
          
          // 设置当前活动状态
          btn.classList.add("active");
          const tabId = btn.getAttribute("data-tab");
          dialog.querySelector(`#tab-${tabId}`).classList.add("active");
        };
      });
      
      // 创建新输入节点按钮
      dialog.querySelector("#create-in-node-btn").onclick = () => {
        document.body.removeChild(dialog);
        this.showCreateNodeDialog("in");
      };
      
      // 创建新输出节点按钮
      dialog.querySelector("#create-out-node-btn").onclick = () => {
        document.body.removeChild(dialog);
        this.showCreateNodeDialog("out");
      };
      
      // 刷新节点列表
      dialog.querySelector("#refresh-nodes-btn").onclick = () => {
        document.body.removeChild(dialog);
        this.showManageNodesDialog();
      };
      
      // 为所有删除按钮添加事件
      dialog.querySelectorAll(".delete-node-btn").forEach(btn => {
        btn.onclick = async (e) => {
          const row = e.target.closest("tr");
          const nodeId = row.getAttribute("data-node-id");
          const nodeGroup = row.getAttribute("data-node-group");
          const nodeName = row.children[0].textContent;
          
          const confirmed = await this.showConfirm(`确定要删除节点 "${nodeName}" 吗？此操作不可撤销。`, "删除确认");
          if (confirmed) {
            try {
              await this.deleteNode(nodeId, nodeGroup);
              row.remove();
              
              // 如果当前类型的tab没有节点了，显示空列表信息
              const tbody = row.parentElement;
              if (tbody.querySelectorAll("tr").length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" class="empty-list">没有创建任何${nodeGroup === "in" ? "输入" : "输出"}节点</td></tr>`;
              }
              
              // 重载页面上的节点
              this.reloadNodes();
            } catch (error) {
              this.showAlert(`删除节点失败: ${error.message}`, "删除失败");
            }
          }
        };
      });
      
      // 添加对话框外部点击和ESC关闭
      this.setupDialogCloseEvents(dialog);
    } catch (error) {
      console.error("[Iyunya Nodes] 获取节点列表失败:", error);
      this.showAlert(`获取节点列表失败: ${error.message}`, "获取失败");
    }
  }
  
  // 创建新节点
  async createNode(name, inputs, dialog, nodeId, nodeType = "in") {
    try {
      const nodeData = {
        name: name,
        inputs: inputs,
        group: nodeType
      };
      
      // 如果提供了节点ID，则添加到请求数据中
      if (nodeId) {
        nodeData.id = nodeId;
      }
      
      const response = await fetch("/api/iyunya/node/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(nodeData)
      });
      
      const result = await response.json();
      
      if (result.status !== "success") {
        throw new Error(result.message || "创建节点失败");
      }
      
      // 关闭对话框
      document.body.removeChild(dialog);
      
      // 显示成功信息，提供刷新选项
      const shouldRefresh = await this.showNodeCreatedAlert(name);
      if (shouldRefresh) {
        // 立即刷新页面
        window.location.reload();
      } else {
        // 只重载节点定义，但不刷新页面
        this.reloadNodes();
      }
      
    } catch (error) {
      console.error("[Iyunya Nodes] 创建节点失败:", error);
      this.showAlert(`创建节点失败: ${error.message}`, "创建失败");
    }
  }
  
  // 删除节点
  async deleteNode(nodeId, nodeGroup = "in") {
    const response = await fetch("/api/iyunya/node/delete", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ 
        id: nodeId,
        group: nodeGroup
      })
    });
    
    const result = await response.json();
    
    if (result.status !== "success") {
      throw new Error(result.message || "删除节点失败");
    }
    
    return result;
  }
  
  // 重新加载节点（刷新界面）
  reloadNodes() {
    // 通知ComfyUI刷新节点列表
    if (app && app.graph) {
      app.graph.clear();
      
      // 触发重新加载节点定义
      const reloadEvent = new CustomEvent("comfy.nodes.changed");
      document.dispatchEvent(reloadEvent);
    } else {
      // 如果app不可用，尝试刷新页面
      window.location.reload();
    }
  }
  
  // 添加对话框样式
  addDialogStyles() {
    // 检查是否已添加样式
    if (document.getElementById("iyunya-dialog-styles")) {
      return;
    }
    
    const style = document.createElement("style");
    style.id = "iyunya-dialog-styles";
    style.textContent = `
      .iyunya-dialog {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
      }
      
      .iyunya-dialog-content {
        background: #222;
        border-radius: 8px;
        width: 500px;
        max-width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
      }
      
      .iyunya-dialog-small {
        width: 400px;
      }
      
      .iyunya-dialog-large {
        width: 700px;
      }
      
      .iyunya-dialog-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        border-bottom: 1px solid #333;
      }
      
      .iyunya-dialog-header h3 {
        margin: 0;
        color: #ddd;
        font-size: 18px;
      }
      
      .iyunya-dialog-close {
        background: none;
        border: none;
        font-size: 24px;
        color: #999;
        cursor: pointer;
      }
      
      .iyunya-dialog-body {
        padding: 20px;
      }
      
      .iyunya-message {
        color: #eee;
        font-size: 16px;
        line-height: 1.5;
        margin-bottom: 10px;
      }
      
      .iyunya-message p {
        margin: 0 0 10px 0;
      }
      
      .iyunya-note {
        color: #ffcc00;
        font-size: 14px;
        padding: 10px;
        background: rgba(255, 204, 0, 0.1);
        border-left: 3px solid #ffcc00;
        margin-top: 10px;
      }
      
      .iyunya-dialog-footer {
        padding: 15px 20px;
        border-top: 1px solid #333;
        display: flex;
        justify-content: flex-end;
        gap: 10px;
      }
      
      .iyunya-form-group {
        margin-bottom: 15px;
      }
      
      .iyunya-form-group label {
        display: block;
        margin-bottom: 5px;
        color: #ccc;
      }
      
      .iyunya-form-group input,
      .iyunya-form-group select {
        width: 100%;
        padding: 8px 10px;
        background: #333;
        border: 1px solid #444;
        border-radius: 4px;
        color: #eee;
        margin-bottom: 8px;
      }
      
      .node-info-row {
        display: flex;
        gap: 10px;
        margin-bottom: 8px;
      }
      
      .node-name-container {
        flex: 2;
      }
      
      .node-id-container {
        flex: 1;
      }
      
      .node-name-container label,
      .node-id-container label {
        display: block;
        margin-bottom: 5px;
        color: #ccc;
      }
      
      .input-param-row {
        display: flex;
        gap: 10px;
        margin-bottom: 8px;
        align-items: center;
      }
      
      .input-param-row .param-name {
        flex: 1;
      }
      
      .input-param-row .param-type {
        width: 140px;
      }
      
      .input-param-row button {
        background: #555;
        border: none;
        color: #eee;
        padding: 5px 10px;
        border-radius: 4px;
        cursor: pointer;
      }
      
      .iyunya-btn {
        background: #555;
        border: none;
        color: #eee;
        padding: 8px 15px;
        border-radius: 4px;
        cursor: pointer;
      }
      
      .iyunya-btn:hover {
        background: #666;
      }
      
      .iyunya-btn-primary {
        background: #0074d9;
      }
      
      .iyunya-btn-primary:hover {
        background: #0063b6;
      }
      
      .iyunya-btn-danger {
        background: #ff4136;
      }
      
      .iyunya-btn-danger:hover {
        background: #e63329;
      }
      
      .iyunya-btn-small {
        padding: 4px 8px;
        font-size: 12px;
      }
      
      .iyunya-table {
        width: 100%;
        border-collapse: collapse;
      }
      
      .iyunya-table th,
      .iyunya-table td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid #333;
      }
      
      .iyunya-table th {
        color: #ddd;
        font-weight: bold;
        background: #2a2a2a;
      }
      
      .empty-list {
        text-align: center;
        color: #888;
        padding: 20px !important;
      }
      
      .iyunya-tabs {
        width: 100%;
      }
      
      .iyunya-tab-buttons {
        display: flex;
        border-bottom: 1px solid #333;
        margin-bottom: 20px;
      }
      
      .iyunya-tab-btn {
        padding: 10px 20px;
        background: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        color: #ccc;
        cursor: pointer;
        font-size: 16px;
      }
      
      .iyunya-tab-btn.active {
        border-bottom-color: #0074d9;
        color: white;
      }
      
      .iyunya-tab-content {
        display: none;
      }
      
      .iyunya-tab-content.active {
        display: block;
      }
    `;
    
    document.head.appendChild(style);
  }
}

// 创建全局实例
let menuInstance = null;

// 主扩展注册
app.registerExtension({
  name: "iyunya.nodes",
  async setup() {
    console.log("Iyunya Nodes 扩展已加载");
    
    try {
      // 等待菜单和按钮组加载
      const waitForButtonGroup = () => {
        return new Promise((resolve) => {
          const checkInterval = setInterval(() => {
            // 查找右侧菜单中的按钮组，特别是包含Manager按钮的那个
            const menuRight = document.querySelector(".comfyui-menu-right");
            if (menuRight) {
              const buttonGroups = menuRight.querySelectorAll(".comfyui-button-group");
              if (buttonGroups.length > 0) {
                // 查找包含Manager按钮的按钮组
                for (const group of buttonGroups) {
                  if (group.querySelector('button[title="ComfyUI Manager"]')) {
                    clearInterval(checkInterval);
                    resolve({menuRight, managerGroup: group});
                    return;
                  }
                }
                // 如果没找到包含Manager的组，使用最后一个按钮组
                clearInterval(checkInterval);
                resolve({menuRight, managerGroup: buttonGroups[buttonGroups.length - 1]});
              }
            }
          }, 100);
        });
      };

      const {menuRight, managerGroup} = await waitForButtonGroup();
      
      // 创建"iyunya"按钮
      const manageButton = document.createElement("button");
      manageButton.id = "iyunya-nodes-button";
      manageButton.textContent = "工作流输入输出";
      manageButton.className = "comfyui-button comfyui-menu-mobile-collapse"; // 添加菜单折叠响应类
      manageButton.title = "Iyunya Nodes Manager"; // 添加tooltip
      manageButton.setAttribute("aria-label", "Iyunya Nodes Manager");
      manageButton.style.fontSize = "14px";
      manageButton.style.background = "linear-gradient(90deg, #6c72cb 0%, #cb69c1 100%)"; // 更改为紫色系渐变
      manageButton.style.color = "white"; // 改为白色文本
      manageButton.style.border = "none";
      manageButton.style.borderRadius = "4px";
      manageButton.style.fontWeight = "500"; // 适当加粗
      manageButton.style.margin = "0 5px"; // 添加左右边距
      
      // 点击事件
      manageButton.onclick = () => {
        if (!menuInstance) {
          menuInstance = new IyunyaNodesMenu();
        }
        menuInstance.showManageNodesDialog();
      };
      
      // 将按钮添加到包含Manager按钮的按钮组中，并放在Manager按钮前面
      const managerButton = managerGroup.querySelector('button[title="ComfyUI Manager"]');
      if (managerButton) {
        managerGroup.insertBefore(manageButton, managerButton);
      } else {
        // 如果找不到Manager按钮，就直接添加到按钮组中
        managerGroup.appendChild(manageButton);
      }
      
      console.log("已添加iyunya按钮到ComfyUI Manager按钮前面");
    } catch (error) {
      console.error("添加按钮失败:", error);
    }
  }
}); 