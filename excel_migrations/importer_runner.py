import os
import sys
from pathlib import Path
import logging
from typing import Any, Dict,Tuple

project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.bootstrap.application_bootstrap import ApplicationBootstrap
from .employee_importer import EmployeeImporter


class ImportRunner:
    
    def __init__(self):

        self.bootstrap = ApplicationBootstrap()
        self.session = self.bootstrap._app_session
        self.mail_service = self.bootstrap.mail_service
        self.importer = EmployeeImporter(self.session, self.mail_service)
        
        # Setup logging
        # self._setup_logging()
    
    def run_import(self, excel_file_path: str):
       
        try:
            
            result = self.importer.import_from_excel(excel_file_path)
            
            self._print_results(result)
            
        except Exception as e:
            self._print_error(f"Unexpected error: {str(e)}")
            logging.error(f"Unexpected error: {str(e)}")
        
        finally:
            self.close()
    
    def close(self):
        self.bootstrap.shutdown()
    
    # ============ PRIVATE METHODS ============
    
    #def _setup_logging(self):

     #   logs_dir = Path(__file__).parent / "logs"
      #  logs_dir.mkdir(exist_ok=True)
        
       # logging.basicConfig(
        #    level=logging.INFO,
         #   format='%(asctime)s - %(levelname)s - %(message)s',
          #  handlers=[
           #     logging.FileHandler(logs_dir / 'import.log',encoding='utf-8'),
            #    logging.StreamHandler()
           # ]
        #)
    
    def _print_results(self, result: dict):

        print(f"\n{'='*50}")
        
        if result['success']:
            print(f" IMPORT DONE!")
            print(f"   Total row: {result.get('total_rows', 0)}")
            print(f"   Success: {result['success_count']} employees")
            print(f"   Error: {result['error_count']}")
        else:
            print(f" IMPORT FAIL!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"  Success: {result['success_count']} employees")
    
    def _print_error(self, message: str):
        print(f" {message}")
    

def main():
    """Main function"""
    
    BASE_DIR = Path(__file__).resolve().parent
    excel_file = BASE_DIR / "Migration_test.xlsx"

    runner = ImportRunner()
    runner.run_import(str(excel_file))

if __name__ == "__main__":
    main()