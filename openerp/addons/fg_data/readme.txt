
1. ȡ�����пͻ���
SELECT
	org.FNumber,
	org.FName,
	org.FContact,
	org.FPhone,
	org.FFax,
	org.FAddress,
	org.FCity,
	org.FProvince,
	org.FCountry,
	item.FName AS Category,
	item.FNumber AS Category_Number
FROM
	t_Organization org
JOIN t_Item item ON item.FItemID = org.FParentID


2.�õ��û���
SELECT
	FUserID,
	FName,
	FForbidden
FROM
	t_User
WHERE
	FSID IS NOT NULL

3. ��ȡ��ҵ����
SELECT
	FNumber,
	FName
FROM
	t_Department;

        
4. ��ȡ��Ʒ��λ��
SELECT
	tmu.FNumber,
	tmu.FName,
	tmu.FCoefficient
FROM
	t_MeasureUnit tmu;
        
5.��ȡ��Ʒ:
SELECT
	icitem.FName,
	icitem.FNumber,
	icitem.FSalePrice,
	icitem.FNote,
	item.FName AS Category_Name,
	item.FNumber AS Category_Num,
	icitem.FModel,
	unit.FNumber AS Unit_Num,
	unit.FName AS Unit_Name,
	dep.FNumber AS Dep_Num,
	dep.FName AS Dep_Name
FROM
	t_icitem icitem
JOIN t_Item item ON item.FItemID = icitem.FParentID
JOIN t_MeasureUnit unit ON unit.FItemID = icitem.FSaleUnitID
JOIN t_Department dep ON dep.FItemID = icitem.FSource;



