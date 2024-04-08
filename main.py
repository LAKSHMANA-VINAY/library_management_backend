from fastapi import FastAPI,HTTPException,status,Response
from bson import ObjectId
from pydantic import BaseModel
from pymongo import MongoClient
from typing import Dict


client=MongoClient("mongodb+srv://pradeepmajji42:Pradeep123@cluster0.mb8pytv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client.student_application
collection_name=db["student_app"]

from pydantic import BaseModel

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address


app=FastAPI()
    
def student_serializer(student: Dict) -> Dict[str, str]:
    return {
        "name": student['name'],
        "age": str(student['age']),
        "address":{
        "city": student['address']['city'],
        "country": student['address']['country']
        }
    }
def get_list_students(student:Dict):
    return {
        "name":student['name'],
        "age":student['age']
    }

def gets_students(students)->list:
    return [get_list_students(student) for student in students]

def students_serializer(students)->list:
    return [student_serializer(student) for student in students]

def student_single_serializer(student_record) -> dict:
        student_record = next(student_record, None)
        return {
            "name": student_record['name'],
            "age": student_record['age'],
            "address": {
                "city": student_record['address'].get('city', ''),
                "country": student_record['address'].get('country', '')
            }
        }


@app.post("/students", response_model=dict,status_code=status.HTTP_201_CREATED)
async def create(student: Student):
    student_dict = student.dict()
    inserted_id = collection_name.insert_one(student_dict).inserted_id
    return {"id": str(inserted_id)}

@app.get("/students")
async def list_students():
    details=gets_students(collection_name.find())
    return {"data":details}

@app.get("/students/{id}")
async def get_student(id:str):
    record=student_single_serializer(collection_name.find({"_id":ObjectId(id)}))
    return record

@app.patch("/students/{id}", status_code=204)
async def patch_student(id: str, student_data: dict):
    student_record = collection_name.find_one({"_id": ObjectId(id)})
    if student_record:
        update_data = {key: value for key, value in student_data.items() if value is not None}
        if update_data:
            collection_name.update_one({"_id": ObjectId(id)}, {"$set": update_data})
            return Response(status_code=204)
        else:
            return {}
    else:
        raise HTTPException(status_code=404, detail="Student not found")
    
@app.delete("/students/{id}")
async def delete_todo(id:str):
    collection_name.find_one_and_delete({"_id":ObjectId(id)})
    return {}