import pandas as pd

class Sheet:
    def __init__(self, url):
        self.url = url
        self.dataFrame = pd.read_excel(self.url)
    
    @property
    def __name__(self):
        name = self.url.split('/')[-1].split('.')[0]
        return f"{name}.{self.__extention__}"
    
    @property
    def __extention__(self):
        return self.url.split('/')[-1].split('.')[-1]
    
    @property
    def heading(self):
        return self.dataFrame.columns.values.tolist()
    
    @property
    def reset_index(self):
        self.dataFrame.reset_index(inplace=True)

    @property
    def __len__(self):
        return len(self.dataFrame)
    
    
    def _zip_heading(self, new_heading, old_heading):
        return zip(new_heading, old_heading)
    
    def rename_heading(self, new_heading_index):
        new_heading = self.dataFrame.iloc[new_heading_index].tolist()
        old_heading = self.heading

        ziped_heading = self._zip_heading(new_heading, old_heading)
        newDict = {}
        for newHead, oldHeading in list(ziped_heading):
            newDict[oldHeading] = newHead

        self.dataFrame.rename(columns=newDict, inplace=True)
        self.dataFrame.drop(new_heading_index, inplace=True)
        self.dataFrame.reset_index(drop=True, inplace=True)

        return self.dataFrame

    def index_y(self, column):
        return self.dataFrame[self.dataFrame.eq(column).any(axis=1)].index[0]
    
    
        

class ExtractSheet(Sheet):
    def __init__(self, url):
        super().__init__(url)

    def remove_unwanted_columns(self, columns, to_index):
        indexs = []
        
        for column in columns:
            indexs.append(self.index_y(column))
        for index in indexs:
            if to_index:
                self.dataFrame.drop(range(index,to_index), inplace=True)
                self.dataFrame.reset_index(drop=True, inplace=True)
            else: 
                self.remove_unwanted_columns_index(index)

        return self.dataFrame
                
    def remove_unwanted_columns_index(self, index):
        self.dataFrame.drop(index, inplace=True)
        self.dataFrame.reset_index(drop=True, inplace=True)
        return self.dataFrame

    
    def replace_nan_value_column(self, column_name, primary_columns=['Batch Semester', 'Day']):        
        prev_value = None
        column_name_value = self.dataFrame[column_name].tolist()
        newColumnValue = []
        for index, value in enumerate(column_name_value):
            if column_name not in primary_columns and index:
                
                
                if self.dataFrame.loc[index, 'Batch Semester'] != self.dataFrame.loc[index - 1, 'Batch Semester']:

                    prev_value = None
            if not pd.isna(value):
                prev_value = value

            newColumnValue.append(prev_value)
        self.dataFrame[column_name] = newColumnValue
        return self.dataFrame
    
    def replace_nan_value_column_all(self):
        for head in self.heading:
            self.replace_nan_value_column(head)
    
    def replace_nan_value_row_all(self):
        newRowArray = []
        prev_value = None
        for index, row in self.dataFrame.iterrows():
            for col_name, value in row.items():
                if not pd.isna(value):
                    prev_value = value
                newRowArray.append(prev_value)
                self.dataFrame.at[index, col_name] = prev_value
        return self.dataFrame
    def replace_nan_value_all(self):
        mask = self.dataFrame.isnull()

        rows_with_nan = self.dataFrame[mask.any(axis=1)]
        columns_with_nan = self.dataFrame.columns[mask.any(axis=0)]

        self.dataFrame[columns_with_nan[0]]
        self.dataFrame.at[rows_with_nan.index[0], columns_with_nan[0]] = 'asdn'

        for column in columns_with_nan:
            for index in rows_with_nan.index:
                self.dataFrame.at[index, column] = self.dataFrame[column][index+1]
        return self.dataFrame
