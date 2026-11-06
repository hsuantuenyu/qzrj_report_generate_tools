import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import duckdb
import pandas as pd
import os
import sys
import shutil
import threading
import warnings
from datetime import datetime
from copy import copy
from tkcalendar import Calendar

# 忽略 pandas 的 DBAPI2 警告
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy')

# ===== 跨平台路径解析 =====
# PyInstaller 打包后，sys._MEIPASS 指向临时解压目录（只读）
# 开发模式下，资源文件在脚本所在目录
_FROZEN = getattr(sys, 'frozen', False)
_RESOURCE_DIR = sys._MEIPASS if _FROZEN else os.path.dirname(os.path.abspath(__file__))


def resolve_resource(filename):
    """解析资源文件路径（只读资源，如 SQL 文件、模板）"""
    return os.path.join(_RESOURCE_DIR, filename)


def get_writable_db_path(db_name):
    """获取可写的数据库路径。
    macOS .app 包内的资源是只读的，需要将数据库复制到可写位置。
    优先查找 .app 同级目录（build_exe.py 复制的文件位置），其次从包内复制。
    """
    if _FROZEN:
        if sys.platform == 'darwin':
            # sys.executable = .app/Contents/MacOS/可执行文件名
            exe_dir = os.path.dirname(sys.executable)
            app_contents_dir = os.path.dirname(exe_dir)   # Contents/
            app_bundle_dir = os.path.dirname(app_contents_dir)  # .app/
            # .app 同级目录 = dist/（build_exe.py 复制文件的位置）
            sibling_dir = os.path.dirname(app_bundle_dir)
        else:
            exe_dir = os.path.dirname(sys.executable)
            sibling_dir = exe_dir

        # 1. 优先检查 .app/可执行文件同级目录是否已有数据库
        candidate = os.path.join(sibling_dir, db_name)
        if os.path.exists(candidate):
            return candidate

        # 2. 检查 .app 同级的 data/ 子目录
        data_dir = os.path.join(sibling_dir, 'data')
        if os.path.isdir(data_dir):
            candidate = os.path.join(data_dir, db_name)
            if os.path.exists(candidate):
                return candidate

        # 3. 以上都没有，创建可写副本
        # 确保 data 目录可写
        try:
            os.makedirs(data_dir, exist_ok=True)
            test_file = os.path.join(data_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except (PermissionError, OSError):
            # 回退到用户数据目录
            if sys.platform == 'darwin':
                data_dir = os.path.join(
                    os.path.expanduser('~/Library/Application Support/前置软件报告生成辅助工具'),
                    'data'
                )
            else:
                data_dir = os.path.join(
                    os.path.expanduser('~'), '.前置软件报告生成辅助工具', 'data'
                )
            os.makedirs(data_dir, exist_ok=True)

        writable_path = os.path.join(data_dir, db_name)

        # 从 PyInstaller 包内复制数据库到可写位置
        resource_db = os.path.join(_RESOURCE_DIR, db_name)
        if not os.path.exists(writable_path) and os.path.exists(resource_db):
            shutil.copy2(resource_db, writable_path)

        return writable_path
    else:
        # 开发模式：直接在脚本所在目录操作
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dev_path = os.path.join(script_dir, db_name)
        try:
            test_file = os.path.join(script_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return dev_path
        except (PermissionError, OSError):
            data_dir = os.path.join(os.path.expanduser('~'), '.前置软件报告生成辅助工具')
            os.makedirs(data_dir, exist_ok=True)
            writable_path = os.path.join(data_dir, db_name)
            if not os.path.exists(writable_path) and os.path.exists(dev_path):
                shutil.copy2(dev_path, writable_path)
            return writable_path


class ReportGeneratorTool:
    def __init__(self, root):
        self.root = root
        self.root.title("前置软件报告生成辅助工具 V1.9")
        
        # 设置窗口大小并居中
        window_width = 700
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.resizable(False, False)
        
        self.db_path = get_writable_db_path("qzrj_quality_report.db")
        self.template_path = None
        self.export_path = None
        self.data_dir = None
        self.start_date = tk.StringVar()
        self.start_date.set("")  # 初始化为空
        self.end_date = tk.StringVar()
        self.end_date.set("")  # 初始化为空
        self.data_imported = False  # 是否已导入数据
        # 机构类型：516 / 1151，决定数据加工与导出时使用的机构标志列
        self.institution_type = tk.StringVar(value='516')

        # 统一设置滚动条样式：宽度32像素，箭头按钮24像素
        style = ttk.Style()
        style.configure("Vertical.TScrollbar", width=32, arrowsize=24)
        style.configure("Horizontal.TScrollbar", width=32, arrowsize=24)
        
        self.create_main_interface()

        # 机构类型变化时同步刷新导出文件名与界面提示
        self.institution_type.trace('w', lambda *args: self.on_institution_type_change())

    def get_flag_column(self):
        """当前机构类型对应的 org_list 机构标志列"""
        return 'is_516_flag' if self.institution_type.get() == '516' else 'is_1151_flag'

    def get_export_base_name(self):
        """当前机构类型对应的导出文件名前缀"""
        if self.institution_type.get() == '1151':
            return "基层_前置软件数据质控报告_1151_质控日期："
        return "疾控中心数据质控报告_质控日期："

    def apply_institution_filter(self, sql):
        """按当前机构类型替换机构标志列（is_516_flag / is_1151_flag）"""
        return sql.replace('is_516_flag', self.get_flag_column())

    def on_institution_type_change(self):
        """机构类型切换后的联动处理"""
        self.update_export_filename()
        self.refresh_type_labels()
        # 汇总表按上一次选择的类型加工，切换后需要重新加工
        if self.data_imported and hasattr(self, 'process_status_label'):
            self.process_status_label.config(
                text="加工状态：机构类型已变更，请重新执行数据加工", foreground="orange")

    def refresh_type_labels(self):
        """刷新各 Tab 中显示的当前机构类型"""
        text = (f"当前机构类型：{self.institution_type.get()}　"
                f"（机构筛选字段：{self.get_flag_column()}）")
        for attr in ('process_type_label', 'export_type_label'):
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.config(text=text)
        
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
        tab5 = ttk.Frame(notebook, padding="10")
        
        notebook.add(tab1, text="1. 数据库测试")
        notebook.add(tab2, text="2. 数据导入")
        notebook.add(tab3, text="3. 数据加工")
        notebook.add(tab4, text="4. 数据导出")
        notebook.add(tab5, text="5. 机构管理")
        
        self.create_db_test_tab(tab1)
        self.create_data_import_tab(tab2)
        self.create_data_process_tab(tab3)
        self.create_data_export_tab(tab4)
        self.create_org_management_tab(tab5)

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
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=3, column=0, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        
        # 垂直滚动条
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文本框
        self.db_info_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15, width=80)
        self.db_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定滚动条
        scrollbar.config(command=self.db_info_text.yview)
        
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
        
        # 设置初始日期为今天
        today = datetime.now().strftime('%Y-%m-%d')
        self.start_date.set(today)
        self.end_date.set(today)
        
        # 开始日期
        start_label = ttk.Label(date_frame, text="开始日期:", font=('微软雅黑', 10, 'bold'))
        start_label.grid(row=0, column=0, padx=5)
        
        start_date_entry = ttk.Entry(date_frame, textvariable=self.start_date, width=12, font=('微软雅黑', 10), state='readonly')
        start_date_entry.grid(row=0, column=1, padx=5)
        
        start_calendar_btn = ttk.Button(date_frame, text="📅", width=3, command=lambda: self.popup_calendar('start'))
        start_calendar_btn.grid(row=0, column=2, padx=2)
        
        start_date_entry.bind('<Button-1>', lambda e: self.popup_calendar('start'))
        
        # 结束日期
        end_label = ttk.Label(date_frame, text="结束日期:", font=('微软雅黑', 10, 'bold'))
        end_label.grid(row=0, column=3, padx=5)
        
        end_date_entry = ttk.Entry(date_frame, textvariable=self.end_date, width=12, font=('微软雅黑', 10), state='readonly')
        end_date_entry.grid(row=0, column=4, padx=5)
        
        end_calendar_btn = ttk.Button(date_frame, text="📅", width=3, command=lambda: self.popup_calendar('end'))
        end_calendar_btn.grid(row=0, column=5, padx=2)
        
        end_date_entry.bind('<Button-1>', lambda e: self.popup_calendar('end'))

        # 机构类型选择（516 / 1151），后续数据加工与导出按此类型筛选机构
        type_label = ttk.Label(date_frame, text="机构类型:", font=('微软雅黑', 10, 'bold'))
        type_label.grid(row=1, column=0, padx=5, pady=(8, 2), sticky=tk.W)

        type_radio_frame = ttk.Frame(date_frame)
        type_radio_frame.grid(row=1, column=1, columnspan=5, sticky=tk.W, pady=(8, 2))

        ttk.Radiobutton(type_radio_frame, text="516 机构", value='516',
                        variable=self.institution_type).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_radio_frame, text="1151 机构（基层）", value='1151',
                        variable=self.institution_type).pack(side=tk.LEFT)

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
        
        # 创建带滚动条的文本框
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=6, column=0, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(6, weight=1)
        
        # 垂直滚动条
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文本框
        self.file_list_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=10, width=80)
        self.file_list_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 绑定滚动条
        scrollbar.config(command=self.file_list_text.yview)
        
    def popup_calendar(self, date_type='start'):
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
        current_date = self.start_date.get() if date_type == 'start' else self.end_date.get()
        if current_date:
            cal.selection_set(current_date)
        
        # 确认选择函数
        def on_confirm():
            selected_date = cal.get_date()
            if date_type == 'start':
                self.start_date.set(selected_date)
            else:
                self.end_date.set(selected_date)
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
        start_date_str = self.start_date.get()
        end_date_str = self.end_date.get()
        if start_date_str and hasattr(self, 'export_name_var'):
            base_name = self.get_export_base_name()
            if start_date_str == end_date_str:
                new_name = f"{base_name}{start_date_str}.xlsx"
            else:
                new_name = f"{base_name}{start_date_str}至{end_date_str}.xlsx"
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

                # 校验 org_list 是否具备当前机构类型对应的标志字段
                flag_column = self.get_flag_column()
                org_columns = [col[1] for col in
                               conn.execute("PRAGMA table_info('org_list')").fetchall()]
                if flag_column not in org_columns:
                    raise Exception(
                        f"org_list 表缺少字段【{flag_column}】，无法按 {self.institution_type.get()} 机构生成报告。\n"
                        "请先在【5. 机构管理】中维护该字段数据。")

                qzrj_files = [f for f in os.listdir(self.data_dir) if f.startswith('qzrj_') and f.endswith('.xlsx')]
                
                if not qzrj_files:
                    raise Exception("未找到以 qzrj_开头的 Excel 文件")
                
                total_files = len(qzrj_files)
                self.import_progress['maximum'] = total_files
                
                self.file_list_text.delete(1.0, tk.END)
                self.file_list_text.insert(tk.END, "开始导入数据...\n")
                self.file_list_text.insert(
                    tk.END,
                    f"当前机构类型：{self.institution_type.get()}（机构筛选字段：{flag_column}）\n")
                
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
                
                self.data_imported = True
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
        
        header_frame = ttk.Frame(frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)

        sql_label = ttk.Label(header_frame, text="执行 加工数据 SQL 脚本")
        sql_label.pack(side=tk.LEFT)

        self.process_type_label = ttk.Label(header_frame, text="")
        self.process_type_label.pack(side=tk.RIGHT)

        self.refresh_type_labels()
        
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
                sql_file = resolve_resource('qzrj_generate_data.sql')
                if not os.path.exists(sql_file):
                    raise Exception(f"找不到 SQL 文件：{sql_file}")
                
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()

                # 按当前机构类型（516 / 1151）替换机构标志列
                flag_column = self.get_flag_column()
                sql_content = self.apply_institution_filter(sql_content)

                self.process_text.insert(tk.END, f"执行 SQL 脚本：{sql_file}\n")
                self.process_text.insert(
                    tk.END,
                    f"当前机构类型：{self.institution_type.get()}（机构筛选字段：{flag_column}）\n\n")
                
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
        
        # 使用当前日期作为默认文件名（日期区间）
        default_date = datetime.now().strftime('%Y-%m-%d')
        default_name = f"{self.get_export_base_name()}{default_date}.xlsx"
        self.export_name_var = tk.StringVar(value=default_name)
        
        # 初始化日期变量
        self.start_date.set(default_date)
        self.end_date.set(default_date)
        export_name_label = ttk.Label(export_frame, text="导出文件名:")
        export_name_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        export_name_entry = ttk.Entry(export_frame, textvariable=self.export_name_var, width=80)
        export_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        export_frame.columnconfigure(1, weight=1)
        
        # ===== 默认导出目录：用户文档目录（可写）=====
        # macOS 上 cwd 通常是只读的 / 或 /Applications，需要使用用户可写目录
        home_documents = os.path.expanduser('~/Documents')
        if os.path.isdir(home_documents) and os.access(home_documents, os.W_OK):
            default_export_dir = home_documents
        elif os.path.isdir(os.path.expanduser('~')) and os.access(os.path.expanduser('~'), os.W_OK):
            default_export_dir = os.path.expanduser('~')
        else:
            default_export_dir = os.path.dirname(os.path.abspath(__file__))

        self._export_dir = default_export_dir

        # 添加路径显示（完整路径 = 目录 + 文件名）
        default_full_path = os.path.join(self._export_dir, default_name)
        self.export_path_var = tk.StringVar(value=default_full_path)
        export_path_label = ttk.Label(export_frame, text="完整路径:")
        export_path_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        export_path_entry = ttk.Entry(export_frame, textvariable=self.export_path_var, width=80)
        export_path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        export_frame.columnconfigure(1, weight=1)

        # 当前机构类型提示（在【2. 数据导入】中切换）
        self.export_type_label = ttk.Label(export_frame, text="")
        self.export_type_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.refresh_type_labels()
        
        # 文件名变化时更新路径（保留目录部分，只替换文件名）
        def update_path(*args):
            filename = self.export_name_var.get()
            self.export_path_var.set(os.path.join(self._export_dir, filename))
        
        self.export_name_var.trace('w', update_path)
        
        # 按钮区：选择保存目录 + 导出 + 打开目录
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, pady=2)

        choose_dir_btn = ttk.Button(btn_frame, text="选择保存目录", command=self.choose_export_dir)
        choose_dir_btn.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(btn_frame, text="开始导出报告", command=self.export_report)
        export_btn.pack(side=tk.LEFT, padx=5)
        
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

    def choose_export_dir(self):
        """选择报告保存目录"""
        directory = filedialog.askdirectory(
            title="选择报告保存目录",
            initialdir=self._export_dir
        )
        if directory:
            self._export_dir = directory
            filename = self.export_name_var.get()
            self.export_path_var.set(os.path.join(directory, filename))
            self.log_message(f"保存目录已设置为：{directory}\n")
            
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
                    '重要建议填字段完整性': self.get_column_level2_sql(),
                    '条件必填字段完整性': self.get_column_level3_sql(),
                    '关联关系明细': self.get_association_sql(),
                    '值域一致性': self.get_dict_sql(),
                    '主诉明细': self.get_chief_sql(),
                    '现病史明细': self.get_present_sql()
                }

                # 按当前机构类型（516 / 1151）替换机构标志列，统一控制各 Sheet 的机构范围
                export_sheets = {name: self.apply_institution_filter(sql)
                                 for name, sql in export_sheets.items()}
                
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
                                # 使用列索引直接获取列字母，避免合并单元格问题
                                from openpyxl.utils import get_column_letter
                                col_letter = get_column_letter(col_idx)
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
                                # 使用列索引直接获取列字母，避免合并单元格问题
                                from openpyxl.utils import get_column_letter
                                col_letter = get_column_letter(col_idx)
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
                
                export_filename = self.export_name_var.get()
                full_path = os.path.join(self._export_dir, export_filename)
                self.log_message(f"\n保存文件到：{full_path}...\n")
                wb.save(full_path)
                
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
        select distinct city,
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
       i_total_records,
       i_notnull_records,
       concat(round((i_notnull_records / i_total_records) * 100, 2), '%') as i_notnull_rate,
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
       sum(i_total_records)                                                            i_total_records,
       sum(i_notnull_records)                                                          i_notnull_records,
       concat(round((sum(i_notnull_records) / sum(i_total_records)) * 100, 2), '%') as i_not_notnull_rate,
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
        注意：此 SQL 已由用户于 2026-09-08 修正，请勿修改！
        详见：导出 SQL 说明.md
        """
        return """
         select distinct a.city,
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
           else concat(g.notnull_rate, '%') end  notnull_rate,
       h.total_records,
       h.notnull_records,
       case
           when h.total_records is null then null
           when h.total_records = 0 then '-'
           else concat(h.notnull_rate, '%') end     notnull_rate,
       i.total_records,
       i.notnull_records,
       case
           when i.total_records is null then null
           when i.total_records = 0 then '-'
           else concat(i.notnull_rate, '%') end     notnull_rate,
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
       l.total_records,
       l.association_records,
       case
           when l.total_records is null then null
           when l.total_records = 0 then '-'
           else concat(l.association_rate, '%') end association_rate,
       m.non_empty_violations,
       m.dict_violations,
       case when m.non_empty_violations is null then null
            when m.non_empty_violations = 0 then '-'
            else concat(m.dict_rate,'%') end dict_rate
from org_list a
         left join qzrj_realtime_org b on b.org_code = a.org_code and b.table_type = '实时表'
         left join qzrj_realtime_org c on c.org_code = a.org_code and c.table_type = '2小时内'
         left join qzrj_realtime_org d on d.org_code = a.org_code and d.table_type = 'T+0内'
         left join qzrj_column_level_org e on e.org_code = a.org_code and e.column_level = '1'
         left join qzrj_column_level_org f on f.org_code = a.org_code and f.column_level = '2'
         left join qzrj_column_level_org g on g.org_code = a.org_code and g.column_level = '3'
         left join qzrj_column_level_org h on h.org_code = a.org_code and h.column_level = 'update_1'
         left join qzrj_column_level_org i on i.org_code = a.org_code and i.column_level = 'update_3'
         left join qzrj_association_org j on j.org_code = a.org_code and j.association_table = 'emr_patient_info'
         left join qzrj_association_org k on k.org_code = a.org_code and k.association_table = 'emr_activity_info'
         left join qzrj_association_org l on l.org_code = a.org_code and l.association_table = 'all'
         left join qzrj_dict_org m on m.org_code = a.org_code
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
    def get_column_level3_sql(self):
        """
        条件必填字段完整性
        注意：此 SQL 新增于2026-05-28
        """
        return """
        select a.city,
       a.org_code,
       a.org_name,
       b.table_name,
       b.table_comment,
       sum(b.total_records) total_records,
       sum(b.notnull_records) notnull_records,
       case
           when sum(b.total_records) is null then null
           when sum(b.total_records) = 0 then '-'
           else
               concat(round((sum(b.notnull_records) / sum(b.total_records)) * 100, 2), '%') end notnull_rate
from org_list a
         left join qzrj_column_level_3_detail b on a.org_code = b.org_code
where a.is_516_flag = '是'
group by a.city,a.org_code,a.org_name,b.table_name,b.table_comment
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

    def create_org_management_tab(self, parent):
        """创建机构管理 Tab"""
        frame = ttk.LabelFrame(parent, text="机构管理", padding="5")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        # 查询区域
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        frame.columnconfigure(0, weight=1)

        search_label = ttk.Label(search_frame, text="搜索：")
        search_label.pack(side=tk.LEFT, padx=5)

        self.org_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.org_search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)

        search_btn = ttk.Button(search_frame, text="查询", command=self.refresh_org_tree)
        search_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(search_frame, text="清空", command=self.clear_org_search)
        clear_btn.pack(side=tk.LEFT, padx=5)

        refresh_btn = ttk.Button(search_frame, text="刷新", command=self.refresh_org_tree)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # 操作按钮区域
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, pady=5)

        add_btn = ttk.Button(btn_frame, text="新增机构", command=self.add_org)
        add_btn.pack(side=tk.LEFT, padx=5)

        edit_btn = ttk.Button(btn_frame, text="编辑机构", command=self.edit_org)
        edit_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = ttk.Button(btn_frame, text="删除机构", command=self.delete_org)
        delete_btn.pack(side=tk.LEFT, padx=5)

        # Treeview 展示区域
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)

        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 水平滚动条
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 定义显示的列
        self.org_tree = ttk.Treeview(tree_frame, columns=('city', 'org_code', 'org_name', 'is_516_flag', 'is_1151_flag', '是否哨点'),
                                     show='headings', yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # 设置列标题和宽度
        self.org_tree.heading('city', text='城市')
        self.org_tree.heading('org_code', text='机构代码')
        self.org_tree.heading('org_name', text='机构名称')
        self.org_tree.heading('is_516_flag', text='是否516')
        self.org_tree.heading('is_1151_flag', text='是否1151')
        self.org_tree.heading('是否哨点', text='是否哨点')

        self.org_tree.column('city', width=80)
        self.org_tree.column('org_code', width=100)
        self.org_tree.column('org_name', width=200)
        self.org_tree.column('is_516_flag', width=80)
        self.org_tree.column('is_1151_flag', width=80)
        self.org_tree.column('是否哨点', width=80)

        self.org_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar.config(command=self.org_tree.yview)
        h_scrollbar.config(command=self.org_tree.xview)

        # 双击编辑
        self.org_tree.bind('<Double-1>', lambda e: self.edit_org())

        # 状态栏
        self.org_status_label = ttk.Label(frame, text="机构管理：未加载")
        self.org_status_label.grid(row=3, column=0, sticky=tk.W, pady=2)

        # 初始加载数据
        self.refresh_org_tree()

    def clear_org_search(self):
        """清空搜索条件并刷新列表"""
        self.org_search_var.set('')
        self.refresh_org_tree()

    def refresh_org_tree(self):
        """刷新机构列表"""
        search_text = self.org_search_var.get().strip()

        try:
            conn = duckdb.connect(self.db_path)

            # 表字段列表（用于适配是否已增加 is_1151_flag 列）
            org_columns = [col[1] for col in
                           conn.execute("PRAGMA table_info('org_list')").fetchall()]
            has_1151 = 'is_1151_flag' in org_columns

            select_columns = ['city', 'org_code', 'org_name', 'is_516_flag']
            if has_1151:
                select_columns.append('is_1151_flag')
            select_columns.append('是否哨点')

            if search_text:
                sql = f"""
                    SELECT {', '.join(select_columns)}
                    FROM org_list
                    WHERE city LIKE '%{search_text}%' 
                       OR org_code LIKE '%{search_text}%' 
                       OR org_name LIKE '%{search_text}%'
                       OR 是否哨点 LIKE '%{search_text}%'
                    ORDER BY city, org_code
                """
            else:
                sql = (f"SELECT {', '.join(select_columns)} FROM org_list"
                       " ORDER BY city, org_code")

            result = conn.execute(sql).fetchall()
            conn.close()

            # 清空现有数据
            for item in self.org_tree.get_children():
                self.org_tree.delete(item)

            # 添加新数据（NULL 值显示为空字符串，缺列时补空值）
            for row in result:
                values = list(row)
                if not has_1151:
                    values.insert(4, '')
                display_row = tuple('' if v is None else v for v in values)
                self.org_tree.insert('', tk.END, values=display_row)

            self.org_status_label.config(text=f"机构管理：共 {len(result)} 条记录", foreground="black")

        except Exception as e:
            self.org_status_label.config(text=f"机构管理：加载失败 - {str(e)}", foreground="red")
            messagebox.showerror("错误", f"加载机构数据失败：\n{str(e)}")

    def add_org(self):
        """新增机构"""
        self.show_org_edit_dialog()

    def edit_org(self):
        """编辑选中的机构"""
        selected = self.org_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选中要编辑的机构")
            return

        item = selected[0]
        values = self.org_tree.item(item, 'values')

        # 获取完整数据
        org_code = values[1]
        try:
            conn = duckdb.connect(self.db_path)
            result = conn.execute(f"SELECT * FROM org_list WHERE org_code = '{org_code}'").fetchone()
            conn.close()

            if result:
                self.show_org_edit_dialog(result)
        except Exception as e:
            messagebox.showerror("错误", f"获取机构数据失败：\n{str(e)}")

    def show_org_edit_dialog(self, org_data=None):
        """显示机构编辑弹窗"""
        top = tk.Toplevel(self.root)
        top.title("编辑机构" if org_data else "新增机构")
        top.resizable(True, True)
        top.attributes('-topmost', True)

        # 计算居中位置
        top.update_idletasks()
        width = 480
        height = 360
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        top.geometry(f"{width}x{height}+{x}+{y}")

        # 两行布局：内容区（可滚动）| 按钮
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)
        top.rowconfigure(1, weight=0)

        # 获取列名
        try:
            conn = duckdb.connect(self.db_path)
            columns = [col[1] for col in conn.execute("PRAGMA table_info('org_list')").fetchall()]
            conn.close()
        except Exception as e:
            messagebox.showerror("错误", f"获取表结构失败：\n{str(e)}")
            top.destroy()
            return

        # 第一行：表单内容区（限制高度，超出自动滚动）
        content_frame = ttk.Frame(top)
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        content_frame.columnconfigure(0, weight=1)

        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(content_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas + Frame 实现滚动
        canvas = tk.Canvas(content_frame, yscrollcommand=v_scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        scrollable_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_canvas_configure(event):
            canvas.itemconfig(scrollable_window, width=event.width)

        canvas.bind('<Configure>', on_canvas_configure)
        v_scrollbar.config(command=canvas.yview)

        # 创建输入控件
        entry_vars = {}
        row_idx = 0

        # 字段中文映射
        FIELD_LABEL_MAP = {
            'city': '地市(州)',
            'org_code': '机构编码',
            'org_name': '机构名称',
            'is_516_flag': '是否516标志',
            'is_1151_flag': '是否1151标志',
            'station_hospital': '是否哨点医院',
            'is_412名单': '是否412名单',
        }
        # 必填字段
        REQUIRED_FIELDS = ['city', 'org_code', 'org_name', 'is_516_flag']
        # 下拉选项字段
        DROPDOWN_FIELDS = ['is_412名单', 'is_516_flag', 'is_1151_flag', '是否哨点', '是否分院区', '是否基层', '是否26', '是否满足实时要求',
                           '是否主院区']

        for col_name in columns:
            display_name = FIELD_LABEL_MAP.get(col_name, col_name)
            is_required = col_name in REQUIRED_FIELDS
            is_dropdown = col_name in DROPDOWN_FIELDS

            # 必填项标签标红（tk.Label 才支持 fg 颜色设置）
            if is_required:
                label = tk.Label(scrollable_frame, text=f"{display_name}：", fg='red')
            else:
                label = ttk.Label(scrollable_frame, text=f"{display_name}：")
            label.grid(row=row_idx, column=0, sticky=tk.W, padx=5, pady=2)

            var = tk.StringVar()
            if org_data and row_idx < len(org_data):
                value = org_data[row_idx]
                var.set(value if value is not None else '')
            entry_vars[col_name] = var

            if is_dropdown:
                # 非必填的下拉框允许选择空值来清空
                combo_values = ("是", "否") if is_required else ("", "是", "否")
                entry = ttk.Combobox(scrollable_frame, textvariable=var, values=combo_values, state="readonly",
                                     width=38)
            else:
                if col_name == 'org_code':
                    vcmd = (top.register(lambda val: val == '' or val.isdigit()), '%P')
                    entry = ttk.Entry(scrollable_frame, textvariable=var, width=40,
                                      validate='key', validatecommand=vcmd)
                else:
                    entry = ttk.Entry(scrollable_frame, textvariable=var, width=40)
            entry.grid(row=row_idx, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

            row_idx += 1

        scrollable_frame.columnconfigure(1, weight=1)

        # 第二行：保存、取消按钮
        btn_frame = ttk.Frame(top)
        btn_frame.grid(row=1, column=0, pady=5)

        def save():
            try:
                # 必填校验
                for field in REQUIRED_FIELDS:
                    if not entry_vars[field].get().strip():
                        display_name = FIELD_LABEL_MAP.get(field, field)
                        top.attributes('-topmost', False)
                        messagebox.showwarning("提示", f"【{display_name}】为必填项，请输入内容", parent=top)
                        top.attributes('-topmost', True)
                        return

                conn = duckdb.connect(self.db_path)

                if org_data:
                    # 获取原始的 org_code（用于 WHERE 条件）
                    original_org_code = org_data[columns.index('org_code')] if 'org_code' in columns else None

                    # 更新：使用原始 org_code 作为 WHERE 条件
                    if original_org_code:
                        set_clause = ", ".join([f"{col} = '{entry_vars[col].get()}'" for col in columns])
                        sql = f"UPDATE org_list SET {set_clause} WHERE org_code = '{original_org_code}'"
                    else:
                        top.attributes('-topmost', False)
                        messagebox.showerror("错误", "无法获取原始机构代码", parent=top)
                        top.attributes('-topmost', True)
                        conn.close()
                        return
                else:
                    # 新增
                    col_str = ", ".join(columns)
                    val_str = ", ".join([f"'{entry_vars[col].get()}'" for col in columns])
                    sql = f"INSERT INTO org_list ({col_str}) VALUES ({val_str})"

                conn.execute(sql)
                conn.commit()
                conn.close()

                top.attributes('-topmost', False)
                messagebox.showinfo("成功", "机构数据保存成功", parent=top)
                top.attributes('-topmost', True)
                top.destroy()
                self.refresh_org_tree()

                # 提示重新数据加工
                if hasattr(self, 'data_imported') and self.data_imported:
                    messagebox.showwarning(
                        "提示",
                        "机构数据已修改，请重新执行数据加工操作。\n\n请切换到【3. 数据加工】选项卡，点击【执行数据加工SQL】按钮。"
                    )

            except Exception as e:
                top.attributes('-topmost', False)
                messagebox.showerror("错误", f"保存失败：\n{str(e)}", parent=top)
                top.attributes('-topmost', True)

        save_btn = ttk.Button(btn_frame, text="保存", command=save)
        save_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = ttk.Button(btn_frame, text="取消", command=top.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)

        top.wait_window()

    def delete_org(self):
        """删除选中的机构"""
        selected = self.org_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选中要删除的机构")
            return

        item = selected[0]
        values = self.org_tree.item(item, 'values')
        org_name = values[2]
        org_code = values[1]

        if messagebox.askyesno("确认删除", f"确定要删除机构【{org_name}】吗？"):
            try:
                conn = duckdb.connect(self.db_path)
                conn.execute(f"DELETE FROM org_list WHERE org_code = '{org_code}'")
                conn.commit()
                conn.close()

                self.refresh_org_tree()
                messagebox.showinfo("成功", "机构删除成功")

                # 提示重新数据加工
                if hasattr(self, 'data_imported') and self.data_imported:
                    messagebox.showwarning(
                        "提示",
                        "机构数据已修改，请重新执行数据加工操作。\n\n请切换到【3. 数据加工】选项卡，点击【执行数据加工SQL】按钮。"
                    )

            except Exception as e:
                messagebox.showerror("错误", f"删除失败：\n{str(e)}")


def main():
    root = tk.Tk()
    app = ReportGeneratorTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
