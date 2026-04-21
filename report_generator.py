import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import duckdb
import pandas as pd
import os
import threading
import warnings
from datetime import datetime
from copy import copy
from tkcalendar import Calendar

# 忽略 pandas 的 DBAPI2 警告
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy')


class ReportGeneratorTool:
    def __init__(self, root):
        self.root = root
        self.root.title("前置软件报告生成辅助工具")
        
        # 设置窗口大小并居中
        window_width = 620
        window_height = 460
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.resizable(False, False)
        
        self.db_path = "qzrj_quality_report.db"
        self.template_path = None
        self.export_path = None
        self.data_dir = None
        self.quality_date = tk.StringVar()
        self.quality_date.set("")  # 初始化为空
        
        self.create_main_interface()
        
    def create_main_interface(self):
        """创建主界面"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        tab1 = ttk.Frame(notebook, padding="10")
        tab2 = ttk.Frame(notebook, padding="10")
        tab3 = ttk.Frame(notebook, padding="10")
        tab4 = ttk.Frame(notebook, padding="10")
        
        notebook.add(tab1, text="1. 数据库测试")
        notebook.add(tab2, text="2. 数据导入")
        notebook.add(tab3, text="3. 数据加工")
        notebook.add(tab4, text="4. 数据导出")
        
        self.create_db_test_tab(tab1)
        self.create_data_import_tab(tab2)
        self.create_data_process_tab(tab3)
        self.create_data_export_tab(tab4)
        
    def create_db_test_tab(self, parent):
        """创建数据库测试 Tab"""
        frame = ttk.LabelFrame(parent, text="DuckDB 数据库连接测试", padding="5")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        db_label = ttk.Label(frame, text=f"数据库文件：{self.db_path}")
        db_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.db_status_label = ttk.Label(frame, text="状态：未测试", foreground="orange")
        self.db_status_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        test_btn = ttk.Button(frame, text="测试数据库连接", command=self.test_database)
        test_btn.grid(row=2, column=0, pady=2)
        
        self.db_info_text = tk.Text(frame, height=15, width=80)
        self.db_info_text.grid(row=3, column=0, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        
    def test_database(self):
        """测试数据库连接"""
        try:
            conn = duckdb.connect(self.db_path)
            result = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='main'").fetchone()
            
            self.db_status_label.config(text="状态：连接成功", foreground="green")
            
            self.db_info_text.delete(1.0, tk.END)
            self.db_info_text.insert(tk.END, f"✓ 数据库连接成功\n")
            self.db_info_text.insert(tk.END, f"✓ 数据库文件：{os.path.abspath(self.db_path)}\n")
            self.db_info_text.insert(tk.END, f"✓ 表数量：{result[0]}\n\n")
            
            tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main' ORDER BY table_name").fetchall()
            self.db_info_text.insert(tk.END, "数据库表列表:\n")
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                self.db_info_text.insert(tk.END, f"  - {table[0]}: {count} 条记录\n")
            
            conn.close()
            
        except Exception as e:
            self.db_status_label.config(text="状态：连接失败", foreground="red")
            self.db_info_text.delete(1.0, tk.END)
            self.db_info_text.insert(tk.END, f"✗ 数据库连接失败\n错误信息：{str(e)}\n")
            
    def create_data_import_tab(self, parent):
        """创建数据导入 Tab"""
        frame = ttk.LabelFrame(parent, text="数据导入", padding="5")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 创建日期选择框架
        date_frame = ttk.Frame(frame)
        date_frame.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        date_label = ttk.Label(date_frame, text="质控日期:", font=('微软雅黑', 10, 'bold'))
        date_label.grid(row=0, column=0, padx=5)
        
        # 设置初始日期为今天
        today = datetime.now().strftime('%Y-%m-%d')
        self.quality_date.set(today)
        
        # 日期显示框（只读）
        date_entry = ttk.Entry(date_frame, textvariable=self.quality_date, width=15, font=('微软雅黑', 10), state='readonly')
        date_entry.grid(row=0, column=1, padx=5)
        
        # 日历选择按钮
        calendar_btn = ttk.Button(date_frame, text="📅", width=3, command=lambda: self.popup_calendar())
        calendar_btn.grid(row=0, column=2, padx=2)
        
        # 绑定鼠标点击事件，点击文本框也弹出日历
        date_entry.bind('<Button-1>', lambda e: self.popup_calendar())
        
        select_btn = ttk.Button(frame, text="选择数据文件目录", command=self.select_data_directory)
        select_btn.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.dir_label = ttk.Label(frame, text="当前目录：未选择")
        self.dir_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        
        
        # 导入按钮框架（居中显示）
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, pady=5)
        import_btn = ttk.Button(btn_frame, text="开始导入数据", command=self.import_data)
        import_btn.pack()
        
        self.import_status_label = ttk.Label(frame, text="导入状态：未开始")
        self.import_status_label.grid(row=4, column=0, sticky=tk.W, pady=2)
        
        self.import_progress = ttk.Progressbar(frame, mode='determinate')
        self.import_progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=2)
    
        frame.columnconfigure(0, weight=1)
        self.file_list_text = tk.Text(frame, height=10, width=80)
        self.file_list_text.grid(row=6, column=0, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        
    def popup_calendar(self):
        """弹出日历选择窗口"""
        # 创建顶级窗口
        top = tk.Toplevel(self.root)
        top.title("选择日期")
        top.resizable(False, False)
        
        # 设置窗口始终在最前
        top.attributes('-topmost', True)
        
        # 获取按钮位置，设置窗口在按钮右侧
        x = self.root.winfo_x() + 280  # 主窗口 X 坐标 + 按钮位置
        y = self.root.winfo_y() + 100  # 主窗口 Y 坐标 + 偏移量
        top.geometry(f"+{x}+{y}")
        
        # 创建 Calendar 控件
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        
        # 设置当前选中的日期
        current_date = self.quality_date.get()
        if current_date:
            cal.selection_set(current_date)
        
        # 确认选择函数
        def on_confirm():
            selected_date = cal.get_date()
            self.quality_date.set(selected_date)
            self.update_export_filename()
            top.destroy()
        
        # 取消选择函数
        def on_cancel():
            top.destroy()
        
        # 创建按钮框架
        btn_frame = ttk.Frame(top)
        btn_frame.pack(pady=5)
        
        # 确认按钮
        confirm_btn = ttk.Button(btn_frame, text="确定", command=on_confirm)
        confirm_btn.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(btn_frame, text="取消", command=on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # 等待窗口关闭
        top.wait_window()
    
    def update_export_filename(self):
        """更新导出文件名中的质控日期"""
        date_str = self.quality_date.get()
        if date_str and hasattr(self, 'export_name_var'):
            # 获取当前文件名（不含日期部分）
            current_name = self.export_name_var.get()
            # 提取基础名称（去掉日期部分）
            base_name = "疾控中心数据质控报告_质控日期："
            new_name = f"{base_name}{date_str}.xlsx"
            self.export_name_var.set(new_name)
    
    def select_data_directory(self):
        """选择数据文件目录"""
        directory = filedialog.askdirectory(title="选择包含 Excel 数据文件的目录")
        if directory:
            self.data_dir = directory
            self.dir_label.config(text=f"当前目录：{directory}")
            
            self.file_list_text.delete(1.0, tk.END)
            self.file_list_text.insert(tk.END, "找到的数据文件:\n")
            
            qzrj_files = [f for f in os.listdir(directory) if f.startswith('qzrj_') and f.endswith('.xlsx')]
            for file in qzrj_files:
                self.file_list_text.insert(tk.END, f"  - {file}\n")
                
            if len(qzrj_files) == 0:
                self.file_list_text.insert(tk.END, "\n未找到以 qzrj_开头的 Excel 文件\n")
                
    def import_data(self):
        """导入数据"""
        if not self.data_dir:
            messagebox.showwarning("警告", "请先选择数据文件目录")
            return
            
        def do_import():
            try:
                conn = duckdb.connect(self.db_path)
                qzrj_files = [f for f in os.listdir(self.data_dir) if f.startswith('qzrj_') and f.endswith('.xlsx')]
                
                if not qzrj_files:
                    raise Exception("未找到以 qzrj_开头的 Excel 文件")
                
                total_files = len(qzrj_files)
                self.import_progress['maximum'] = total_files
                
                self.file_list_text.delete(1.0, tk.END)
                self.file_list_text.insert(tk.END, "开始导入数据...\n")
                
                # 排除不需要导入的表
                skip_tables = ['qzrj_present_detail']
                
                for i, file in enumerate(qzrj_files):
                    table_name = os.path.splitext(file)[0]
                    
                    # 跳过不需要导入的表
                    if table_name in skip_tables:
                        self.file_list_text.insert(tk.END, f"跳过：{file} (不需要导入)\n")
                        self.root.update_idletasks()
                        continue
                    
                    file_path = os.path.join(self.data_dir, file)
                    
                    self.file_list_text.insert(tk.END, f"导入：{file} -> {table_name}\n")
                    self.root.update_idletasks()
                    
                    try:
                        df = pd.read_excel(file_path)
                        
                        conn.execute(f"DELETE FROM {table_name}")
                        
                        insert_sql = f"INSERT INTO {table_name} SELECT * FROM df"
                        conn.execute(insert_sql)
                        
                        self.import_progress['value'] = i + 1
                        self.root.update_idletasks()
                        
                        self.file_list_text.insert(tk.END, f"  ✓ 成功导入 {len(df)} 条记录\n")
                        
                    except Exception as e:
                        self.file_list_text.insert(tk.END, f"  ✗ 导入失败：{str(e)}\n")
                        raise
                    
                conn.commit()
                conn.close()
                
                self.import_status_label.config(text="导入状态：完成", foreground="green")
                messagebox.showinfo("成功", f"成功导入 {total_files} 个数据表")
                
            except Exception as e:
                self.import_status_label.config(text="导入状态：失败", foreground="red")
                messagebox.showerror("错误", f"数据导入失败:\n{str(e)}")
                
        thread = threading.Thread(target=do_import)
        thread.start()
        
    def create_data_process_tab(self, parent):
        """创建数据加工 Tab"""
        frame = ttk.LabelFrame(parent, text="数据加工", padding="5")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        sql_label = ttk.Label(frame, text="执行 加工数据 SQL 脚本")
        sql_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.process_status_label = ttk.Label(frame, text="加工状态：未开始")
        self.process_status_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        process_btn = ttk.Button(frame, text="执行数据加工 SQL", command=self.process_data)
        process_btn.grid(row=2, column=0, pady=2)
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=3, column=0, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        
        # 垂直滚动条
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文本框 (缩小高度)
        self.process_text = tk.Text(text_frame, height=12, width=80, yscrollcommand=scrollbar.set)
        self.process_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定滚动条
        scrollbar.config(command=self.process_text.yview)
        
    def process_data(self):
        """执行数据加工 SQL"""
        def do_process():
            try:
                self.process_status_label.config(text="加工状态：执行中...", foreground="orange")
                self.process_text.delete(1.0, tk.END)
                
                # 从 qzrj_generate_data.sql 文件读取 SQL
                sql_file = 'qzrj_generate_data.sql'
                if not os.path.exists(sql_file):
                    raise Exception(f"找不到 SQL 文件：{sql_file}")
                
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                self.process_text.insert(tk.END, f"执行 SQL 脚本：{sql_file}\n\n")
                
                conn = duckdb.connect(self.db_path)
                
                # 改进 SQL 分割逻辑，处理多行 SQL 语句
                statements = []
                current_stmt = []
                for line in sql_content.split('\n'):
                    line = line.strip()
                    if line.startswith('--'):
                        continue
                    if line.endswith(';'):
                        current_stmt.append(line[:-1])
                        full_stmt = ' '.join(current_stmt).strip()
                        if full_stmt:
                            statements.append(full_stmt)
                        current_stmt = []
                    elif line:
                        current_stmt.append(line)
                
                if current_stmt:
                    full_stmt = ' '.join(current_stmt).strip()
                    if full_stmt:
                        statements.append(full_stmt)
                
                success_count = 0
                error_count = 0
                
                for i, stmt in enumerate(statements):
                    stmt = stmt.strip()
                    if stmt:
                        try:
                            result = conn.execute(stmt)
                            if result:
                                rows_affected = result.rowcount
                                self.process_text.insert(tk.END, f"✓ 语句 {i+1}: 成功")
                                if rows_affected >= 0:
                                    self.process_text.insert(tk.END, f" (影响 {rows_affected} 行)\n")
                                else:
                                    self.process_text.insert(tk.END, f"\n")
                                success_count += 1
                            else:
                                self.process_text.insert(tk.END, f"✓ 语句 {i+1}: 成功\n")
                                success_count += 1
                        except Exception as e:
                            self.process_text.insert(tk.END, f"✗ 语句 {i+1} 失败：{str(e)[:200]}\n")
                            error_count += 1
                
                conn.commit()
                
                self.process_text.insert(tk.END, f"\n执行统计：成功 {success_count} 条，失败 {error_count} 条\n")
                
                # 查询生成的汇总数据表 (包括 qzrj_city_summary)
                result = conn.execute("""
                    SELECT table_name FROM information_schema.tables WHERE table_schema='main' AND table_name
in('qzrj_association_org', 'qzrj_column_level_org', 'qzrj_dict_org', 'qzrj_realtime_org','qzrj_city_summary')
                """).fetchall()
                
                self.process_text.insert(tk.END, f"\n✓ 生成的汇总数据表:\n")
                for table in result:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                    self.process_text.insert(tk.END, f"  - {table[0]}: {count} 条记录\n")
                
                conn.close()
                
                self.process_status_label.config(text="加工状态：完成", foreground="green")
                
            except Exception as e:
                self.process_status_label.config(text="加工状态：失败", foreground="red")
                self.process_text.insert(tk.END, f"\n✗ 错误：{str(e)}\n")
                
        thread = threading.Thread(target=do_process)
        thread.start()
        
    def create_data_export_tab(self, parent):
        """创建数据导出 Tab"""
        frame = ttk.LabelFrame(parent, text="数据导出", padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 模板文件区域
        template_frame = ttk.LabelFrame(frame, text="模板文件", padding="5")
        template_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        frame.columnconfigure(0, weight=1)
        
        self.template_label = ttk.Label(template_frame, text="模板文件：未选择")
        self.template_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        select_template_btn = ttk.Button(template_frame, text="选择模板文件", command=self.select_template)
        select_template_btn.grid(row=0, column=1, padx=5)
        
        # 导出设置区域
        export_frame = ttk.LabelFrame(frame, text="导出设置", padding="5")
        export_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        frame.columnconfigure(0, weight=1)
        
        # 使用当前质控日期作为默认文件名
        default_date = datetime.now().strftime('%Y-%m-%d')
        default_name = f"疾控中心数据质控报告_质控日期：{default_date}.xlsx"
        self.export_name_var = tk.StringVar(value=default_name)
        export_name_label = ttk.Label(export_frame, text="导出文件名:")
        export_name_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        export_name_entry = ttk.Entry(export_frame, textvariable=self.export_name_var, width=80)
        export_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        export_frame.columnconfigure(1, weight=1)
        
        # 添加路径显示
        self.export_path_var = tk.StringVar(value=os.path.abspath(default_name))
        export_path_label = ttk.Label(export_frame, text="完整路径:")
        export_path_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        export_path_entry = ttk.Entry(export_frame, textvariable=self.export_path_var, width=80)
        export_path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        export_frame.columnconfigure(1, weight=1)
        
        # 文件名变化时更新路径
        def update_path(*args):
            filename = self.export_name_var.get()
            self.export_path_var.set(os.path.abspath(filename))
        
        self.export_name_var.trace('w', update_path)
        
        # 导出按钮
        export_btn = ttk.Button(frame, text="开始导出报告", command=self.export_report)
        export_btn.grid(row=2, column=0, pady=2)
        
        self.export_status_label = ttk.Label(frame, text="导出状态：未开始")
        self.export_status_label.grid(row=3, column=0, sticky=tk.W, pady=1)
        
        self.export_progress = ttk.Progressbar(frame, mode='indeterminate')
        self.export_progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=1)
        frame.columnconfigure(0, weight=1)
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=5, column=0, pady=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(5, weight=1)
        
        # 垂直滚动条
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文本框
        self.export_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15, width=80)
        self.export_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定滚动条
        scrollbar.config(command=self.export_text.yview)
    
    def log_message(self, message):
        """输出日志并自动滚动到最新消息"""
        self.export_text.insert(tk.END, message)
        self.export_text.see(tk.END)  # 自动滚动到最新消息
        self.root.update_idletasks()
        
    def select_template(self):
        """选择模板文件"""
        file_path = filedialog.askopenfilename(
            title="选择 Excel 模板文件",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file_path:
            self.template_path = file_path
            self.template_label.config(text=f"模板文件：{os.path.basename(file_path)}")
            
    def export_report(self):
        """导出报告"""
        if not self.template_path:
            messagebox.showwarning("警告", "请先选择模板文件")
            return
            
        def do_export():
            try:
                from openpyxl import load_workbook
                
                self.export_status_label.config(text="导出状态：处理中...", foreground="orange")
                self.export_progress.start()
                self.export_text.delete(1.0, tk.END)
                
                self.log_message("加载模板文件...\n")
                wb = load_workbook(self.template_path)
                
                self.log_message("连接数据库...\n")
                conn = duckdb.connect(self.db_path)
                
                export_sheets = {
                    '地市(州)': self.get_city_state_sql(),
                    '机构汇总': self.get_org_summary_sql(),
                    '时效性明细': self.get_realtime_detail_sql(),
                    '必填字段完整性': self.get_column_level1_sql(),
                    '关键建议填字段完整性': self.get_column_level2_sql(),
                    '关联关系明细': self.get_association_sql(),
                    '值域一致性': self.get_dict_sql(),
                    '主诉明细': self.get_chief_sql(),
                    '现病史明细': self.get_present_sql()
                }
                
                total_sheets = len(export_sheets)
                processed = 0
                
                for sheet_idx, (sheet_name, sql) in enumerate(export_sheets.items(), 1):
                    try:
                        self.log_message(f"\n[{sheet_idx}/{total_sheets}] 处理 Sheet: {sheet_name}...\n")
                        
                        if sheet_name in wb.sheetnames:
                            ws = wb[sheet_name]
                            
                            self.log_message(f"  执行 SQL 查询...\n")
                            self.root.update_idletasks()
                            
                            df = pd.read_sql_query(sql, conn)
                            record_count = len(df)
                            self.log_message(f"  查询到 {record_count} 条记录\n")
                            self.root.update_idletasks()
                            
                            start_row = 4
                        
                        # 优化写入操作：批量写入
                        if record_count > 0:
                            # 使用 append 方法批量写入，比逐个单元格写入快 10-100 倍
                            values = df.values.tolist()
                            
                            # 检查第一行是否是合计行
                            has_total_row = False
                            total_row_data = None
                            if len(values) > 0 and values[0][0] in ['Total', '合计']:
                                has_total_row = True
                                total_row_data = values[0]  # 保存合计行数据
                                # 将第一列的值修改为"合计"
                                total_row_data[0] = '合计'
                                values = values[1:]  # 移除第一行合计
                                record_count = len(values)
                            
                            # 批量追加数据 (先写数据行)
                            for row_values in values:
                                ws.append(row_values)
                            
                            # 在末尾写入合计行
                            if has_total_row and total_row_data:
                                # 导入样式模块
                                from openpyxl.styles import Font, PatternFill, Alignment
                                
                                # 黄色背景填充
                                yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
                                # 粗体字体
                                bold_font = Font(bold=True)
                                # 居中对齐
                                center_alignment = Alignment(horizontal='center', vertical='center')
                                
                                # 写入合计行到最后一行
                                ws.append(total_row_data)
                                total_row = ws.max_row
                                
                                # 应用黄色背景、粗体字体和居中对齐到合计行
                                for col_idx in range(1, len(total_row_data) + 1):
                                    cell = ws.cell(row=total_row, column=col_idx)
                                    cell.fill = yellow_fill
                                    cell.font = bold_font
                                    # 除 A 列外都居中对齐
                                    if col_idx > 1:
                                        cell.alignment = center_alignment
                                
                                self.log_message(f"  ✓ 已创建合计行（黄色背景、粗体）\n")
                            
                            # 设置地市(州)Sheet 页的对齐方式：除 A 列外所有单元格居中
                            if sheet_name == '地市(州)':
                                from openpyxl.styles import Alignment
                                center_alignment = Alignment(horizontal='center', vertical='center')
                                
                                # 遍历所有数据行（从第 4 行到最后一行）
                                for row_idx in range(start_row, ws.max_row + 1):
                                    # 从 B 列开始（第 2 列）到最后一列
                                    for col_idx in range(2, ws.max_column + 1):
                                        cell = ws.cell(row=row_idx, column=col_idx)
                                        cell.alignment = center_alignment
                            
                            self.log_message(f"  写入完成，共 {record_count} 条记录\n")
                            
                            processed += 1
                            self.log_message(f"  ✓ 导出成功\n")
                            self.root.update_idletasks()
                        else:
                            self.log_message(f"  ✗ Sheet 不存在，跳过\n")
                            self.root.update_idletasks()
                            
                    except Exception as e:
                        self.log_message(f"  ✗ 错误：{str(e)}\n")
                        import traceback
                        self.log_message(f"  {traceback.format_exc()}\n")
                
                conn.close()
                
                # 设置列宽 (在地市 (州)Sheet 页之后)
                self.log_message(f"\n设置列宽...\n")
                
                for sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                    
                    # 地市 (州)Sheet 页使用自定义列宽
                    if sheet_name == '地市 (州)':
                        # 地市 (州)Sheet 页：A 列（地市）列宽 12，B 列开始根据表头设置
                        try:
                            ws.column_dimensions['A'].width = 12  # 地市
                            # 遍历其他列，根据第 3 行的表头设置列宽
                            for col_idx in range(2, ws.max_column + 1):
                                col_letter = ws.cell(row=1, column=col_idx).column_letter
                                header_value = ws.cell(row=3, column=col_idx).value
                                
                                if header_value:
                                    header_str = str(header_value)
                                    if '机构编码' in header_str or 'org_code' in header_str.lower():
                                        ws.column_dimensions[col_letter].width = 12
                                    elif '机构名称' in header_str or 'org_name' in header_str.lower():
                                        ws.column_dimensions[col_letter].width = 24
                            
                            self.log_message(f"  ✓ {sheet_name}: 已设置列宽\n")
                        except Exception as e:
                            self.log_message(f"  ✗ {sheet_name}: 列宽设置失败 - {str(e)}\n")
                    else:
                        # 其他 Sheet 页：根据列名设置列宽
                        try:
                            # 遍历所有列
                            for col_idx in range(1, ws.max_column + 1):
                                col_letter = ws.cell(row=1, column=col_idx).column_letter
                                header_value = ws.cell(row=3, column=col_idx).value
                                
                                # 根据列名设置列宽
                                if header_value:
                                    header_str = str(header_value)
                                    if '机构编码' in header_str or 'org_code' in header_str.lower():
                                        ws.column_dimensions[col_letter].width = 12
                                        self.log_message(f"  ✓ {sheet_name}: {header_str} 列宽设置为 12\n")
                                    elif '机构名称' in header_str or 'org_name' in header_str.lower():
                                        ws.column_dimensions[col_letter].width = 24
                                        self.log_message(f"  ✓ {sheet_name}: {header_str} 列宽设置为 24\n")
                                    elif any(keyword in header_str for keyword in 
                                             ['表名称', '表注释', '关联表名称', '关联表注释', 
                                              '列名称', '列注释', 'table_name', 'table_comment',
                                              'column_name', 'column_comment']):
                                        ws.column_dimensions[col_letter].width = 29
                                        self.log_message(f"  ✓ {sheet_name}: {header_str} 列宽设置为 29\n")
                            
                            self.log_message(f"  ✓ {sheet_name}: 已设置列宽\n")
                        except Exception as e:
                            self.log_message(f"  ✗ {sheet_name}: 列宽设置失败 - {str(e)}\n")
                
                self.root.update_idletasks()
                
                # 设置单元格对齐方式：指定列居中
                self.log_message(f"\n设置对齐方式...\n")
                
                # 需要居中的列名关键词
                center_keywords = [
                    '纳入统计记录数', '达标数据量', '达标率',
                    '不为空记录数', '完整率', '关联记录数', '关联率',
                    '纳入统计数据条数', '值域在有效范围的数据条数', '值域在有效范围的数据占比',
                    '达标机构数', '达标率 (%)'
                ]
                
                for sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                    
                    try:
                        from openpyxl.styles import Alignment
                        
                        # 创建居中对齐样式
                        center_alignment = Alignment(horizontal='center', vertical='center')
                        
                        # 遍历第 3 行（表头行）查找需要居中的列
                        for col_idx in range(1, ws.max_column + 1):
                            header_value = ws.cell(row=3, column=col_idx).value
                            
                            if header_value:
                                header_str = str(header_value)
                                # 检查是否包含需要居中的关键词
                                if any(keyword in header_str for keyword in center_keywords):
                                    col_letter = ws.cell(row=1, column=col_idx).column_letter
                                    
                                    # 设置该列所有数据单元格居中（从第 4 行开始）
                                    for row_idx in range(4, ws.max_row + 1):
                                        cell = ws.cell(row=row_idx, column=col_idx)
                                        cell.alignment = center_alignment
                                    
                                    self.log_message(f"  ✓ {sheet_name}: {header_str} 已设置居中\n")
                    except Exception as e:
                        pass  # 忽略错误，继续处理
                
                self.root.update_idletasks()
                
                export_path = self.export_name_var.get()
                full_path = os.path.abspath(export_path)
                self.log_message(f"\n保存文件到：{full_path}...\n")
                wb.save(export_path)
                
                self.export_progress.stop()
                self.export_status_label.config(text="导出状态：完成", foreground="green")
                self.log_message(f"\n✓ 报告已成功导出到：{full_path}\n")
                self.log_message(f"✓ 共处理 {processed}/{total_sheets} 个 Sheet 页\n")
                
                # 显示带滚动条的消息框
                messagebox.showinfo("报告生成","导出成功！")
                
            except Exception as e:
                self.export_progress.stop()
                self.export_status_label.config(text="导出状态：失败", foreground="red")
                import traceback
                error_msg = f"错误：{str(e)}\n\n{traceback.format_exc()}"
                self.log_message(f"\n{error_msg}\n")
                messagebox.showerror("错误", f"导出失败:\n{str(e)}")
                
        thread = threading.Thread(target=do_export)
        thread.start()
    
    def show_scrollable_messagebox(self, title, message):
        """显示带垂直滚动条的消息框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=20, width=70)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text_widget.yview)
        
        # 插入消息内容
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)  # 设为只读
        
        # 添加按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=(0, 20))
        
        ok_btn = ttk.Button(btn_frame, text="确定", command=dialog.destroy)
        ok_btn.pack()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        dialog.wait_window()
        
    def get_city_state_sql(self):
        """
        地市州汇总 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
        select city,
       org_cnt,
       real_cnt,
       concat(round((real_cnt / org_cnt) * 100, 2), '%')                  as real_rate,
       hour_cnt,
       concat(round((hour_cnt / org_cnt) * 100, 2), '%')                  as hour_rate,
       other_cnt,
       concat(round((other_cnt / org_cnt) * 100, 2), '%')                 as other_rate,
       e_total_records,
       e_notnull_records,
       concat(round((e_notnull_records / e_total_records) * 100, 2), '%') as e_notnull_rate,
       f_total_records,
       f_notnull_records,
       concat(round((f_notnull_records / f_total_records) * 100, 2), '%') as f_notnull_rate,
       g_total_records,
       g_notnull_records,
       concat(round((g_notnull_records / g_total_records) * 100, 2), '%') as g_notnull_rate,
       h_total_records,
       h_notnull_records,
       concat(round((h_notnull_records / h_total_records) * 100, 2), '%') as h_notnull_rate,
       association_org_cnt,
       concat(round((association_org_cnt / org_cnt) * 100, 2), '%')       as association__rate,
       dict_org_cnt,
       concat(round((dict_org_cnt / org_cnt) * 100, 2), '%')              as dict_rate
from qzrj_city_summary a
union
select 'Total'                                                                            city,
       sum(org_cnt),
       sum(real_cnt),
       concat(round((sum(real_cnt) / sum(org_cnt)) * 100, 2), '%')                  as real_rate,
       sum(hour_cnt)                                                                   hour_cnt,
       concat(round((sum(hour_cnt) / sum(org_cnt)) * 100, 2), '%')                  as hour_rate,
       sum(other_cnt)                                                                  other_cnt,
       concat(round((sum(other_cnt) / sum(org_cnt)) * 100, 2), '%')                 as other_rate,
       sum(e_total_records)                                                            e_total_records,
       sum(e_notnull_records)                                                          e_notnull_records,
       concat(round((sum(e_notnull_records) / sum(e_total_records)) * 100, 2), '%') as e_notnull_rate,
       sum(f_total_records)                                                            f_total_records,
       sum(f_notnull_records)                                                          f_notnull_records,
       concat(round((sum(f_notnull_records) / sum(f_total_records)) * 100, 2), '%') as f_notnull_rate,
       sum(g_total_records) g_total_records,
       sum(g_notnull_records)  g_notnull_records,
       concat(round((sum(g_notnull_records) / sum(g_total_records)) * 100, 2), '%') as g_notnull_rate,
       sum(h_total_records) h_total_records,
       sum(h_notnull_records) h_notnull_records,
       concat(round((sum(h_notnull_records) / sum(h_total_records)) * 100, 2), '%') as h_notnull_rate,
       sum(association_org_cnt)                                                        association_org_cnt,
       concat(round((sum(association_org_cnt) / sum(org_cnt)) * 100, 2), '%')       as association__rate,
       sum(dict_org_cnt)                                                               dict_org_cnt,
       concat(round((sum(dict_org_cnt) / sum(org_cnt)) * 100, 2), '%')              as dict_rate
from qzrj_city_summary
order by city
        """
        
    def get_org_summary_sql(self):
        """
        机构汇总 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
         select a.city,
       a.org_code,
       a.org_name,
       b.total_recods,
       b.compliance_records,
       case
           when b.total_recods is null then null
           when b.total_recods = 0 then '-'
           else concat(b.compliance_rate, '%') end  compliance_rate,
       c.total_recods,
       c.compliance_records,
       case
           when c.total_recods is null then null
           when c.total_recods = 0 then '-'
           else concat(c.compliance_rate, '%') end  compliance_rate,
       d.total_recods,
       d.compliance_records,
       case
           when d.total_recods is null then null
           when d.total_recods = 0 then '-'
           else concat(d.compliance_rate, '%') end  compliance_rate,
       e.total_records,
       e.notnull_records,
       case
           when e.total_records is null then null
           when e.total_records = 0 then '-'
           else concat(e.notnull_rate, '%') end     notnull_rate,
       f.total_records,
       f.notnull_records,
       case
           when f.total_records is null then null
           when f.total_records = 0 then '-'
           else concat(f.notnull_rate, '%') end     notnull_rate,
       g.total_records,
       g.notnull_records,
       case
           when g.total_records is null then null
           when g.total_records = 0 then '-'
           else concat(f.notnull_rate, '%') end     notnull_rate,
       h.total_records,
       h.notnull_records,
       case
           when h.total_records is null then null
           when h.total_records = 0 then '-'
           else concat(h.notnull_rate, '%') end     notnull_rate,
       i.total_records,
       i.association_records,
       case
           when i.total_records is null then null
           when i.total_records = 0 then '-'
           else concat(i.association_rate, '%') end association_rate,
       j.total_records,
       j.association_records,
       case
           when j.total_records is null then null
           when j.total_records = 0 then '-'
           else concat(j.association_rate, '%') end association_rate,
       k.total_records,
       k.association_records,
       case
           when k.total_records is null then null
           when k.total_records = 0 then '-'
           else concat(k.association_rate, '%') end association_rate,
       l.non_empty_violations,
       l.dict_violations,
       case when l.non_empty_violations is null then null
            when l.non_empty_violations = 0 then '-'
            else concat(l.dict_rate,'%') end dict_rate
from org_list a
         left join qzrj_realtime_org b on b.org_code = a.org_code and b.table_type = '实时表'
         left join qzrj_realtime_org c on c.org_code = a.org_code and c.table_type = '2小时内'
         left join qzrj_realtime_org d on d.org_code = a.org_code and d.table_type = 'T+0内'
         left join qzrj_column_level_org e on e.org_code = a.org_code and e.column_level = '1'
         left join qzrj_column_level_org f on f.org_code = a.org_code and f.column_level = '2'
         left join qzrj_column_level_org g on g.org_code = a.org_code and g.column_level = 'update_1'
         left join qzrj_column_level_org h on h.org_code = a.org_code and h.column_level = 'update_3'
         left join qzrj_association_org i on i.org_code = a.org_code and i.association_table = 'emr_patient_info'
         left join qzrj_association_org j on j.org_code = a.org_code and j.association_table = 'emr_activity_info'
         left join qzrj_association_org k on k.org_code = a.org_code and k.association_table = 'all'
         left join qzrj_dict_org l on l.org_code = a.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code
        """
        
    def get_realtime_detail_sql(self):
        """
        时效性明细 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
         select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       b.table_type,
       b.total_records,
       b.compliance_records,
       case
           when total_records is null then null
           when total_records = 0 then '-'
           else
               concat(b.compliance_rate, '%') end compliance_rate,
       b.table_flag
from org_list a
         left join qzrj_realtime_detail b on a.org_code = b.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code
        """
        
    def get_column_level1_sql(self):
        """
        必填字段完整性 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
        select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       b.total_records,
       b.notnull_records,
       case
           when total_records is null then null
           when total_records = 0 then '-'
           else
               concat(b.notnull_rate, '%') end notnull_rate
from org_list a
    left join qzrj_column_level_1_detail b on a.org_code = b.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code
        """
        
    def get_column_level2_sql(self):
        """
        关键建议填字段完整性 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
        select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       b.total_records,
       b.notnull_records,
       case
           when total_records is null then null
           when total_records = 0 then '-'
           else
               concat(b.notnull_rate, '%') end notnull_rate
from org_list a
         left join qzrj_column_level_2_detail b on a.org_code = b.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code
        """
        
    def get_association_sql(self):
        """
        关联关系明细 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
        select a.city,a.org_code,a.org_name,
       b.table_name,
       b.table_comment,
       b.association_table,
       b.association_table_comment,
       b.total_records,
       b.association_records,
       case when total_records = 0 then '-'
           else
               concat( b.association_rate,'%')
           end association_rate
       from org_list a
    left join  qzrj_association_detail b on b.org_code = a.org_code
where a.is_516_flag ='是'
order by a.city,a.org_code
        """
        
    def get_dict_sql(self):
        """
        值域一致性 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
        select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       b.field_name,
       b.field_comment,
       b.non_empty_violations,
       b.dict_violations,
       case
           when b.non_empty_violations is null then null
           when b.non_empty_violations = 0 then '-'
           else concat(b.dict_rate, '%') end dict_rate
from org_list a
         left join qzrj_dict_detail b on b.org_code = a.org_code
where a.is_516_flag = '是'
order by a.city, a.org_code
        """
        
    def get_chief_sql(self):
        """
        主诉明细 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
        select a.city,
       a.org_code,
       a.org_name,
       a.是否哨点,
       b.table_name,
       b.table_comment,
       b.field_name,
       b.field_comment,
       b.total_records,
       b.notnull_records,
       case
           when b.total_records = 0 then '-'
           else
               concat(b.notnull_rate, '%')
           end notnull_rate
from org_list a
         left join qzrj_chief_detail b on b.org_code = a.org_code and b.field_name = 'chief_complaint'
where a.is_516_flag = '是'
order by a.city, a.org_code
        """
        
    def get_present_sql(self):
        """
        现病史明细 SQL
        注意：此 SQL 已由用户于 2026-04-19 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
        select a.city,
       a.org_code,
       a.org_name,
       a.是否哨点,
       b.table_name,
       b.table_comment,
       b.field_name,
       b.field_comment,
       b.total_records,
       b.notnull_records,
       case
           when b.total_records = 0 then '-'
           else
               concat(b.notnull_rate, '%')
           end notnull_rate
from org_list a
         left join qzrj_chief_detail b on b.org_code = a.org_code and b.field_name = 'present_illness_his'
where a.is_516_flag = '是'
order by a.city, a.org_code
        """


def main():
    root = tk.Tk()
    app = ReportGeneratorTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
